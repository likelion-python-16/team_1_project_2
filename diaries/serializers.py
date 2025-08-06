from rest_framework import serializers
from .models import DiaryEntry
from summaries.serializers import DailySummarySerializer
from users.models import User

class DiaryEntrySerializer(serializers.ModelSerializer):
    user_uuid = serializers.UUIDField(write_only=True, help_text="일기를 작성한 사용자의 UUID")
    summary = serializers.SerializerMethodField(read_only=True)  # 감정 요약 포함

    text = serializers.CharField(
        max_length=255,
        help_text="일기 내용 (255자 이내)",
    )
    emotion = serializers.CharField(
        max_length=30,
        required=False,
        allow_blank=True,
        help_text="감정 상태 (예: 행복, 슬픔 등)"
    )

    class Meta:
        model = DiaryEntry
        fields = ['id', 'user_uuid', 'text', 'emotion', 'created_at', 'summary']
        read_only_fields = ['id', 'created_at', 'summary']

    def create(self, validated_data):
        validated_data.pop('user_uuid', None)  # 뷰에서 이미 user 할당했으므로 제거
        return DiaryEntry.objects.create(**validated_data)

    def validate_text(self, value):
        if not value.strip():
            raise serializers.ValidationError("내용은 빈값일 수 없습니다.")
        if len(value) > 255:
            raise serializers.ValidationError("내용은 255자 이내여야 합니다.")
        return value

    def get_summary(self, obj):
        try:
            summary = obj.daily_summary  # 역참조, DiaryEntry → DailySummary
            return DailySummarySerializer(summary).data
        except Exception:
            return None
