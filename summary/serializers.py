from rest_framework import serializers
from .models import EmotionDiary, DiaryRecord


class EmotionDiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionDiary
        fields = '__all__'


class DiaryRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiaryRecord
        fields = '__all__'
