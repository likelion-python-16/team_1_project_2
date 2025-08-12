
from rest_framework import serializers
from .models import User, DiaryEntry, DailySummary

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "created_at"]

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
