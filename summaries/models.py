import uuid
from django.db import models
from django.conf import settings

class DailySummary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    diary_entry = models.OneToOneField(
        'diaries.DiaryEntry',
        related_name='daily_summary',
        on_delete=models.CASCADE,
        help_text="요약 대상 일기와 1:1 관계"
    )
    emotion = models.CharField(max_length=30, help_text="요약된 감정 상태")
    summary = models.TextField(help_text="일기의 감정 요약 텍스트")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.diary_entry.user.email} - {self.created_at.date()} 요약"
