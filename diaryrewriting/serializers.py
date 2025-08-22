# diaryrewriting/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DiaryEntry, DailySummary, SummaryHistory

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source="date_joined", read_only=True)
    class Meta:
        model = User
        fields = ["id", "created_at", "username"]

class DiaryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryEntry
        fields = ["id", "user", "content", "timestamp", "emotion", "lat", "lng"]
        read_only_fields = ["id", "timestamp"]

class DailySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySummary
        fields = ["id", "user", "date", "summary_text", "emotion", "recommended_items", "diary_text"]
        read_only_fields = ["id"]

class SummaryHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SummaryHistory
        fields = ["id", "user", "date", "summary_text", "emotion", "meta", "created_at"]
        read_only_fields = ["id", "created_at", "user"]