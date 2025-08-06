from rest_framework import serializers
from .models import DailySummary

class DailySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySummary
        fields = ['emotion', 'summary', 'created_at'] # 출력할 필드 목록
        read_only_fields = ['emotion', 'summary', 'created_at'] # 읽기 전용 필드
