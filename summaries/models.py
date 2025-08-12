import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class DailySummary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_summaries",
        help_text="요약의 주인 유저",
        null=True,       # 임시로 null 허용
        blank=True,
    )
    date = models.DateField(default=timezone.now, help_text="요약 날짜")
    emotion = models.CharField(max_length=50, help_text="요약된 감정 상태")
    summary = models.TextField(help_text="일기의 감정 요약 텍스트")
    recommended_items = models.JSONField(null=True, blank=True, help_text="추천 콘텐츠 (옵션)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']
        verbose_name = "Daily Summary"
        verbose_name_plural = "Daily Summaries"

    def __str__(self):
        return f"{self.user.email if self.user else 'Unknown User'} - {self.date} 요약"
