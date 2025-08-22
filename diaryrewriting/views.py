# diaryrewriting/views.py (관련 부분만)
from datetime import date
from typing import List
from django.db.models.functions import TruncDate
from django.db.models import Count
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import DiaryEntry, DailySummary, SummaryHistory
from .serializers import (
    DiaryEntrySerializer, DailySummarySerializer, UserSerializer, SummaryHistorySerializer
)
from .utils import get_or_create_user, attach_uid_cookie

# HF 기반
from .services.hf_emotion import predict_emotions
from .services.hf_summarizer import summarize_korean
from .services.emotion_aggregate import pick_overall_emotion

User = get_user_model()

@api_view(["GET"])
@permission_classes([AllowAny])
def whoami(request):
    user = get_or_create_user(request)
    data = UserSerializer(user).data
    resp = Response(data, status=200)
    attach_uid_cookie(resp, user)
    return resp

@api_view(["POST"])
@permission_classes([AllowAny])
def create_entry(request):
    user = get_or_create_user(request)
    payload = request.data.copy()
    payload["user"] = user.pk
    ser = DiaryEntrySerializer(data=payload)
    if ser.is_valid():
        entry = ser.save()
        resp = Response(DiaryEntrySerializer(entry).data, status=status.HTTP_201_CREATED)
        attach_uid_cookie(resp, user)
        return resp
    return Response(ser.errors, status=400)

@api_view(["GET"])
@permission_classes([AllowAny])
def list_entries(request):
    user = get_or_create_user(request)
    d_str = request.GET.get("date")
    qs = DiaryEntry.objects.filter(user=user)
    if d_str:
        try:
            target = date.fromisoformat(d_str)
            qs = qs.filter(timestamp__date=target)
        except ValueError:
            return Response({"detail": "Invalid date. Use YYYY-MM-DD."}, status=400)
    data = DiaryEntrySerializer(qs.order_by("-timestamp"), many=True).data
    resp = Response(data, status=200)
    attach_uid_cookie(resp, user)
    return resp

@api_view(["GET"])
@permission_classes([AllowAny])
def list_days(request):
    user = get_or_create_user(request)
    qs = (
        DiaryEntry.objects
        .filter(user=user)
        .annotate(day=TruncDate("timestamp"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("-day")
    )
    resp = Response(list(qs), status=200)
    attach_uid_cookie(resp, user)
    return resp

# ✅ 요약 생성 (그날 일기 DB에서 읽어 HF로 분석 → DailySummary upsert + SummaryHistory 적재)
@api_view(["POST"])
@permission_classes([AllowAny])
def finalize_day_summary(request):
    user = get_or_create_user(request)
    d_str = (request.data or {}).get("date")
    try:
        d = date.fromisoformat(d_str) if d_str else date.today()
    except ValueError:
        return Response({"detail": "Invalid date. Use YYYY-MM-DD."}, status=400)

    entries = DiaryEntry.objects.filter(user=user, timestamp__date=d).order_by("timestamp")
    texts: List[str] = [e.content for e in entries]

    if not texts:
        # 일기 없으면 빈 요약 upsert (또는 404 반환도 가능)
        obj, _ = DailySummary.objects.update_or_create(
            user=user, date=d,
            defaults={"summary_text": "", "emotion": "", "recommended_items": [], "diary_text": ""},
        )
        data = DailySummarySerializer(obj).data
        resp = Response(data, status=200)
        attach_uid_cookie(resp, user)
        return resp

    # 1) 문장별 감정 (배치)
    emo_preds = predict_emotions(texts)  # [{'label','score'}, ...]
    overall_emotion = pick_overall_emotion(emo_preds)

    # 2) 요약 (문장 합쳐서 한 번에)
    joined = "\n".join(texts)
    summary_text = summarize_korean(joined, max_new_tokens=160)

    # 3) upsert (일자별 1건)
    obj, _ = DailySummary.objects.update_or_create(
        user=user, date=d,
        defaults={
            "summary_text": summary_text,
            "emotion": overall_emotion,
            "recommended_items": [],
            "diary_text": joined,
        },
    )

    # 4) 히스토리 적재 (버전 기록)
    SummaryHistory.objects.create(
        user=user,
        date=d,
        summary_text=summary_text,
        emotion=overall_emotion,
        meta={"entry_emotions": emo_preds},
    )

    data = DailySummarySerializer(obj).data
    # 필요 시 문장별 감정도 함께 반환(옵션)
    data["entry_emotions"] = emo_preds

    resp = Response(data, status=200)
    attach_uid_cookie(resp, user)
    return resp

# ✅ 요약 조회 (없으면 404 → FE는 '요약 없음' 표시)
@api_view(["GET"])
@permission_classes([AllowAny])
def get_summary(request):
    user = get_or_create_user(request)
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
    resp = Response(data, status=200)
    attach_uid_cookie(resp, user)
    return resp