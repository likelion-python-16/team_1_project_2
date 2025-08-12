
from datetime import date
from typing import List

from django.db.models.functions import TruncDate
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import User, DiaryEntry, DailySummary
from .serializers import DiaryEntrySerializer, DailySummarySerializer, UserSerializer
from .utils import get_or_create_user, attach_uid_cookie
from .services.openai_service import summarize

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
    payload["user"] = str(user.id)
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
    qs = (DiaryEntry.objects
          .filter(user=user)
          .annotate(day=TruncDate("timestamp"))
          .values("day")
          .annotate(count=Count("id"))
          .order_by("-day"))
    resp = Response(list(qs), status=200)
    attach_uid_cookie(resp, user)
    return resp

@api_view(["POST"])
@permission_classes([AllowAny])
def generate_summary(request):
    user = get_or_create_user(request)
    d_str = request.data.get("date")
    if not d_str:
        d = date.today()
    else:
        try:
            d = date.fromisoformat(d_str)
        except ValueError:
            return Response({"detail": "Invalid date. Use YYYY-MM-DD."}, status=400)
    entries = DiaryEntry.objects.filter(user=user, timestamp__date=d).order_by("timestamp")
    texts: List[str] = [e.content for e in entries]
    summary_text, emotion, items, diary_text = summarize(texts, d)
    obj, created = DailySummary.objects.update_or_create(
        user=user, date=d,
        defaults={
            "summary_text": summary_text,
            "emotion": emotion,
            "recommended_items": items,
            "diary_text": diary_text,
        },
    )
    data = DailySummarySerializer(obj).data
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
