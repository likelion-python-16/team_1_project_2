# diaryrewriting/views.py
from datetime import date
from typing import List

from django.db.models.functions import TruncDate
from django.db.models import Count
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

# ❌ from .models import User, DiaryEntry, DailySummary
from .models import DiaryEntry, DailySummary
from .serializers import DiaryEntrySerializer, DailySummarySerializer, UserSerializer
from .utils import get_or_create_user, attach_uid_cookie


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
    payload["user"] = user.pk  # PK 타입 그대로 전달 (int/uuid 등)
    ser = DiaryEntrySerializer(data=payload)
    if ser.is_valid():
        entry = ser.save()
        resp = Response(DiaryEntrySerializer(entry).data, status=status.HTTP_201_CREATED)
        attach_uid_cookie(resp, user)
        return resp
    return Response(ser.errors, status=status.HTTP_400_BAD_REQUEST)


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

@api_view(["POST"])
@permission_classes([AllowAny])
def finalize_day_summary(request):
    """
    버튼 클릭 시 호출:
    body: { "date": "YYYY-MM-DD" }  (없으면 오늘)
    동작: 해당 날짜의 DiaryEntry를 모두 DB에서 가져와
         1) 문장별 감정 분류(배치)
         2) 하루 텍스트 요약
         3) 대표 감정 산출
         → DailySummary upsert 후 반환
    """
    user = get_or_create_user(request)
    d_str = (request.data or {}).get("date")
    try:
        d = date.fromisoformat(d_str) if d_str else date.today()
    except ValueError:
        return Response({"detail": "Invalid date. Use YYYY-MM-DD."}, status=400)

    # DB에서 그날 일기들 로드
    entries = DiaryEntry.objects.filter(user=user, timestamp__date=d).order_by("timestamp")
    texts: List[str] = [e.content for e in entries]

    if not texts:
        # 일기가 없으면 비어있는 DailySummary라도 만들어 반환(선택)
        obj, _ = DailySummary.objects.update_or_create(
            user=user, date=d,
            defaults={"summary_text": "", "emotion": "", "recommended_items": [], "diary_text": ""},
        )
        data = DailySummarySerializer(obj).data
        resp = Response(data, status=200)
        attach_uid_cookie(resp, user)
        return resp

    # 1) 문장별 감정(배치)
    emo_preds = predict_emotions(texts)  # [{'label','score'}, ...]
    overall_emotion = pick_overall_emotion(emo_preds)

    # 2) 요약(문장 합쳐서 한 번에)
    joined = "\n".join(texts)
    summary_text = summarize_korean(joined, max_new_tokens=160)

    # 3) 원문 보관(옵션)
    diary_text = joined

    # 4) upsert
    obj, _ = DailySummary.objects.update_or_create(
        user=user, date=d,
        defaults={
            "summary_text": summary_text,
            "emotion": overall_emotion,
            "recommended_items": [],  # 필요 시 규칙/모델로 채우기
            "diary_text": diary_text,
        },
    )
    data = DailySummarySerializer(obj).data
    # 프론트 편의를 위해 문장별 감정도 함께 내려주기(옵션)
    data["entry_emotions"] = emo_preds

    resp = Response(data, status=200)
    attach_uid_cookie(resp, user)
    return resp

@api_view(["POST"])
@permission_classes([AllowAny])
def generate_diary(request):
    # alias for generate_summary, more semantic for FE
    return generate_summary(request)


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


@api_view(["GET"])
@permission_classes([AllowAny])
def get_diary(request):
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

    resp = Response({"date": str(d), "diary_text": obj.diary_text or ""}, status=200)
    attach_uid_cookie(resp, user)
    return resp
