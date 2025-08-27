# coupangapi/serializers.py
from rest_framework import serializers
from .models import Recommendation

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ["user", "date", "base_emotion", "items", "created_at"]
        read_only_fields = ["user", "created_at"]