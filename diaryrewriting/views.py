# diaryrewriting/views.py

from datetime import date
from typing import List, Dict, Any
import os

from django.db import transaction
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.db.models import Count
from django.contrib.auth import get_user_model

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, time, timedelta
from .models import DiaryEntry, DailySummary, SummaryHistory
from .serializers import (
    DiaryEntrySerializer, DailySummarySerializer, UserSerializer, SummaryHistorySerializer
)

# HF 기반
from .services.hf_emotion import predict_emotions
from .services.hf_summarizer import summarize_korean
from .services.emotion_aggregate import pick_overall_emotion

User = get_user_model()


# -------------------------------
# 인증된 사용자 정보 확인
# -------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def whoami(request):
    data = UserSerializer(request.user).data
    return Response(data, status=200)


# -------------------------------
# 일기 작성
# -------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_entry(request):
    user = request.user
    payload = request.data.copy()
    payload["user"] = user.pk
    ser = DiaryEntrySerializer(data=payload)
    if ser.is_valid():
        entry = ser.save()
        return Response(DiaryEntrySerializer(entry).data, status=status.HTTP_201_CREATED)
    return Response(ser.errors, status=400)


# -------------------------------
# ✅ 한 줄 일기 단건 조회
# -------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def retrieve_entry(request, pk: int):
    user = request.user
    try:
        entry = DiaryEntry.objects.get(pk=pk, user=user)
    except DiaryEntry.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)
    return Response(DiaryEntrySerializer(entry).data, status=200)


# -------------------------------
# ✅ 한 줄 일기 수정 (PUT/PATCH)
# -------------------------------
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_entry(request, pk: int):
    user = request.user
    try:
        entry = DiaryEntry.objects.get(pk=pk, user=user)
    except DiaryEntry.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    # 허용 필드만 업데이트 (content, timestamp 정도만 권장)
    payload = request.data.copy()
    # 사용자가 바꿀 수 없도록 강제
    payload.pop("user", None)
    payload.pop("id", None)

    ser = DiaryEntrySerializer(entry, data=payload, partial=(request.method == "PATCH"))
    if ser.is_valid():
        entry = ser.save()
        return Response(DiaryEntrySerializer(entry).data, status=200)
    return Response(ser.errors, status=400)


# -------------------------------
# ✅ 한 줄 일기 삭제
# -------------------------------
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_entry(request, pk: int):
    user = request.user
    deleted, _ = DiaryEntry.objects.filter(pk=pk, user=user).delete()
    if not deleted:
        return Response({"detail": "Not found"}, status=404)
    return Response(status=204)


# -------------------------------
# 일기 리스트 조회 (날짜별)
# -------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_entries(request):
    user = request.user
    d_str = request.GET.get("date")

    print(f"DEBUG >>> user: id={user.id}, username={user.username}")

    qs = DiaryEntry.objects.filter(user=user)

    if d_str:
        try:
            target = date.fromisoformat(d_str)

            # ✅ KST 기준 자정~자정
            tz = timezone.get_current_timezone()  # Asia/Seoul
            start = timezone.make_aware(datetime.combine(target, time.min), tz)
            end = start + timedelta(days=1)

            qs = qs.filter(timestamp__gte=start, timestamp__lt=end)

            print(f"DEBUG >>> date range: {start.isoformat()} ~ {end.isoformat()}")
        except ValueError:
            return Response({"detail": "Invalid date. Use YYYY-MM-DD."}, status=400)

    qs = qs.order_by("-timestamp")
    data = DiaryEntrySerializer(qs, many=True).data
    print(f"DEBUG >>> entries count={len(data)} first={data[0] if data else None}")
    return Response(data, status=200)

# -------------------------------
# 일기 작성된 날 목록
# -------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_days(request):
    user = request.user
    qs = (
        DiaryEntry.objects
        .filter(user=user)
        .annotate(day=TruncDate("timestamp"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("-day")
    )
    return Response(list(qs), status=200)


# -------------------------------
# 안전한 요약 호출
# -------------------------------
def _safe_summarize_korean(text: str, max_new_tokens: int) -> str:
    try:
        return summarize_korean(text, max_new_tokens=max_new_tokens)
    except Exception:
        return ""


# -------------------------------
# 개별 엔트리 요약 (원문만 요약)
# -------------------------------
def _summarize_entries_with_emotions(
    entries: List[DiaryEntry], emo_preds: List[Dict[str, Any]], per_summary_tokens: int = 80
) -> List[Dict[str, str]]:
    """
    summarize_korean이 '입력 텍스트만 요약'하므로
    시간/감정 같은 메타 문구는 붙이지 않고 원문만 넣는다.
    시간/감정 정보는 응답 JSON에 별도로 유지한다.
    """
    entry_summaries: List[Dict[str, str]] = []
    for e, emo in zip(entries, emo_preds):
        t = timezone.localtime(e.timestamp).strftime("%H:%M")
        in_text = e.content  # ✅ 프롬프트/지시문 없이 원문만 전달
        snippet = _safe_summarize_korean(in_text, max_new_tokens=per_summary_tokens) or e.content[:120]
        entry_summaries.append({
            "time": t,
            "emotion": emo.get("label", "중립"),
            "summary": snippet.strip()
        })
    return entry_summaries


# -------------------------------
# 엔트리 요약 → 하루 전체 요약 (지시문 없이 요약)
# -------------------------------
def _meta_summary_from_entries(entry_summaries: List[Dict[str, str]], max_tokens: int = 160) -> str:
    """
    1차 엔트리 요약들을 간단히 나열한 텍스트를 만들고,
    그 텍스트 자체를 다시 '순수 요약'한다.
    (프롬프트/지시문 금지)
    """
    # 시간 정보를 남기되, 과한 마크업/대괄호 등은 사용하지 않는다.
    merged = "\n".join(f"{x['time']} - {x['summary']}" for x in entry_summaries)
    # ✅ 지시문 없이 합친 텍스트 자체를 요약
    return _safe_summarize_korean(merged, max_new_tokens=max_tokens)


# -------------------------------
# ✅ 하루 요약 생성 API
# -------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def finalize_day_summary(request):
    user = request.user

    # 날짜 파싱 (요청 없으면 현지 시간 기준 '오늘')
    d_str = (request.data or {}).get("date")
    if d_str:
        try:
            d = date.fromisoformat(d_str)
        except ValueError:
            return Response({"detail": "Invalid date. Use YYYY-MM-DD."}, status=400)
    else:
        now_local = timezone.localtime(timezone.now())
        d = now_local.date()

    # 해당 날짜의 모든 일기
    entries = (DiaryEntry.objects
               .filter(user=user, timestamp__date=d)
               .order_by("timestamp"))
    texts: List[str] = [e.content for e in entries]

    # 일기 없음 → 빈 요약 upsert
    if not texts:
        obj, _ = DailySummary.objects.update_or_create(
            user=user, date=d,
            defaults={"summary_text": "", "emotion": "", "recommended_items": [], "diary_text": ""},
        )
        data = DailySummarySerializer(obj).data
        data["entry_emotions"] = []
        data["entry_summaries"] = []
        return Response(data, status=200)

    # 1) 감정 추정 + 대표 감정
    try:
        emo_preds = predict_emotions(texts)  # [{'label','score'}, ...]
        overall_emotion = pick_overall_emotion(emo_preds)
    except Exception:
        emo_preds = [{"label": "중립", "score": 0.0} for _ in texts]
        overall_emotion = "중립"

    # 2) 엔트리별 요약 (원문만 요약)
    entry_summaries = _summarize_entries_with_emotions(entries, emo_preds, per_summary_tokens=80)

    # 3) 하루 메타 요약 (지시문 없이)
    final_summary = _meta_summary_from_entries(entry_summaries, max_tokens=160)

    # 4) upsert + 이력 기록
    joined = "\n".join(e.content for e in entries)  # 원문 백업용
    with transaction.atomic():
        obj, _ = DailySummary.objects.update_or_create(
            user=user, date=d,
            defaults={
                "summary_text": final_summary,
                "emotion": overall_emotion,
                "recommended_items": [],
                "diary_text": joined,
            },
        )
        SummaryHistory.objects.create(
            user=user,
            date=d,
            summary_text=final_summary,
            emotion=overall_emotion,
            meta={"entry_emotions": emo_preds, "entry_summaries": entry_summaries},
        )

    # 5) 응답
    data = DailySummarySerializer(obj).data
    data["entry_emotions"] = emo_preds
    data["entry_summaries"] = entry_summaries
    return Response(data, status=200)


# -------------------------------
# ✅ 하루 요약 조회 API
# -------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_summary(request):
    user = request.user
    d_str = request.GET.get("date")
    if not d_str:
        return Response({"detail": "date query param required"}, status=400)
    try:
        d = date.fromisoformat(d_str)
    except ValueError:
        return Response({"detail": "Invalid date. Use YYYY-MM-DD."}, status=400)

    try:
        obj = DailySummary.objects.get(user=user, date=d)
    except DailySummary.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)

    data = DailySummarySerializer(obj).data
    return Response(data, status=200)