# coupangapi/models.py
from django.db import models
from django.conf import settings

class Recommendation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cp_recommendations",
    )
    date = models.DateField(db_index=True)
    base_emotion = models.CharField(max_length=32, blank=True, default="")
    items = models.JSONField(default=list)  # 검색 링크/상품 리스트 캐시
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "date")]
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"CPRec(user={self.user_id}, date={self.date}, emotion={self.base_emotion})"