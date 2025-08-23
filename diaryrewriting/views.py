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

from .models import DiaryEntry, DailySummary, SummaryHistory
from .serializers import (
    DiaryEntrySerializer, DailySummarySerializer, UserSerializer, SummaryHistorySerializer
)

# HF 기반
from .services.hf_emotion import predict_emotions
from .services.hf_summarizer import summarize_korean
from .services.emotion_aggregate import pick_overall_emotion

User = get_user_model()

MODEL_SUM = os.getenv("HF_SUMMARY_MODEL", "gogamza/kobart-summarization")
IS_KOBART = "kobart" in MODEL_SUM.lower()


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
# 일기 리스트 조회 (날짜별)
# -------------------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_entries(request):
    user = request.user
    d_str = request.GET.get("date")
    qs = DiaryEntry.objects.filter(user=user)
    if d_str:
        try:
            target = date.fromisoformat(d_str)
            qs = qs.filter(timestamp__date=target)
        except ValueError:
            return Response({"detail": "Invalid date. Use YYYY-MM-DD."}, status=400)
    data = DiaryEntrySerializer(qs.order_by("-timestamp"), many=True).data
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
# 개별 엔트리 요약
# -------------------------------
def _summarize_entries_with_emotions(
    entries: List[DiaryEntry], emo_preds: List[Dict[str, Any]], per_summary_tokens: int = 80
) -> List[Dict[str, str]]:
    entry_summaries: List[Dict[str, str]] = []
    for e, emo in zip(entries, emo_preds):
        t = timezone.localtime(e.timestamp).strftime("%H:%M")
        if IS_KOBART:
            # KoBART는 지시문 제거: 컨텍스트만
            in_text = f"{t} {emo.get('label','중립')}. {e.content}"
        else:
            # Instruction 모델만 지시문 사용
            in_text = (
                f"시간 {t}, 감정 {emo.get('label','중립')}. "
                "다음 내용을 한국어로 1~2문장으로 요약하라:\n"
                f"{e.content}"
            )
        snippet = _safe_summarize_korean(in_text, max_new_tokens=per_summary_tokens) or e.content[:120]
        entry_summaries.append({
            "time": t,
            "emotion": emo.get("label", "중립"),
            "summary": snippet.strip()
        })
    return entry_summaries


# -------------------------------
# 엔트리 요약 → 하루 전체 요약
# -------------------------------
def _meta_summary_from_entries(entry_summaries: List[Dict[str, str]], max_tokens: int = 160) -> str:
    bullets = "\n".join(
        f"- {x['time']} / 감정 {x['emotion']} : {x['summary']}" for x in entry_summaries
    )
    if IS_KOBART:
        # KoBART: 지시문 없이 bullets만
        prompt = bullets
    else:
        # Instruction 모델: 지시문 허용
        prompt = (
            "아래 항목들을 시간 순으로 자연스럽게 2~3문단 한국어 요약으로 정리하라. "
            "감정의 변화가 드러나도록 연결하고, 중복은 제거하며 핵심 사건 위주로:\n"
            f"{bullets}"
        )
    return _safe_summarize_korean(prompt, max_new_tokens=max_tokens)


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

    # 2) 엔트리별 요약
    entry_summaries = _summarize_entries_with_emotions(entries, emo_preds, per_summary_tokens=80)

    # 3) 하루 메타 요약
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