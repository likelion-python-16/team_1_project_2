# diaryrewriting/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DiaryEntry, DailySummary

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    # 기본 User에는 created_at이 없으므로 date_joined를 created_at 이름으로 노출
    created_at = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta:
        model = User
        fields = ["id", "created_at"]  # 필요하면 "username", "email"도 추가 가능


class DiaryEntrySerializer(serializers.ModelSerializer):
    # 작성자를 뷰에서 request.user로 주입할 거면 읽기 전용으로 두는 걸 권장
    # user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DiaryEntry
        fields = ["id", "user", "content", "timestamp", "emotion", "lat", "lng"]
        read_only_fields = ["id", "timestamp"]
        # 만약 user를 항상 서버에서 세팅한다면: read_only_fields = ["id", "timestamp", "user"]


class DailySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySummary
        fields = ["id", "user", "date", "summary_text", "emotion", "recommended_items", "diary_text"]
        read_only_fields = ["id"]
