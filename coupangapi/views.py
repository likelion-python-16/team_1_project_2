# coupangapi/views.py
from datetime import date as date_cls
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from diaryrewriting.models import DailySummary
from .models import Recommendation
from .serializers import RecommendationSerializer
from .services.recommender import keywords_for_emotion
from .services.link_builder import build_links_for_keyword

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_or_refresh_recommendation(request):
    """
    body: {"date": "YYYY-MM-DD", "limit": 8 (optional)}
    DailySummary에서 대표 감정 읽고 → 감정별 키워드 → 각 엔진 검색 링크 생성 → 캐시 upsert
    """
    user = request.user
    d_str = (request.data or {}).get("date")
    if not d_str:
        return Response({"detail": "date required (YYYY-MM-DD)"}, status=400)
    try:
        d = date_cls.fromisoformat(d_str)
    except ValueError:
        return Response({"detail": "Invalid date. Use YYYY-MM-DD."}, status=400)

    try:
        summ = DailySummary.objects.get(user=user, date=d)
    except DailySummary.DoesNotExist:
        return Response({"detail": "DailySummary not found for given date."}, status=404)

    emotion = (summ.emotion or "").strip() or "중립"
    limit = int((request.data or {}).get("limit") or (request.GET.get("limit") or 8))

    items = []
    for kw in keywords_for_emotion(emotion):
        items.extend(build_links_for_keyword(kw))
        if len(items) >= limit:
            break
    items = items[:limit]

    with transaction.atomic():
        rec, _created = Recommendation.objects.update_or_create(
            user=user, date=d,
            defaults={"base_emotion": emotion, "items": items},
        )
    return Response(RecommendationSerializer(rec).data, status=200)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_recommendation(request):
    user = request.user
    d_str = request.GET.get("date")
    if not d_str:
        return Response({"detail": "date required (YYYY-MM-DD)"}, status=400)
    try:
        d = date_cls.fromisoformat(d_str)
    except ValueError:
        return Response({"detail": "Invalid date. Use YYYY-MM-DD."}, status=400)

    rec = get_object_or_404(Recommendation, user=user, date=d)
    return Response(RecommendationSerializer(rec).data, status=200)