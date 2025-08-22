# diaryrewriting/models.py
from django.conf import settings
from django.db import models

class DiaryEntry(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="entries"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # 감정은 나중에 자동분석으로 적재하고 싶다면 사용(선택)
    emotion = models.CharField(max_length=50, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user_id} {self.timestamp:%F %T} {self.content[:20]}"


class DailySummary(models.Model):
    """
    날짜별 최종 요약 1건(대표 감정/요약/원문).
    - 요약 페이지는 이 테이블 기준으로 '있음/없음' 판단
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="summaries"
    )
    date = models.DateField()  # YYYY-MM-DD
    summary_text = models.TextField(blank=True)
    emotion = models.CharField(max_length=50, blank=True)
    recommended_items = models.JSONField(null=True, blank=True)
    diary_text = models.TextField(null=True, blank=True)  # 하루 텍스트 합본(옵션)

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["user", "date"]),
        ]

    def __str__(self):
        return f"{self.user_id} {self.date} ({self.emotion})"


class SummaryHistory(models.Model):
    """
    요약을 생성/갱신할 때마다 한 건씩 쌓이는 버전 히스토리(감정/요약/부가정보).
    최신 created_at이 최신 요약 시도.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="summary_histories",
    )
    date = models.DateField()
    summary_text = models.TextField(blank=True)
    emotion = models.CharField(max_length=50, blank=True)
    # 문장별 감정 결과, 생성 파라미터 등 부가정보 저장에 유용
    meta = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "date", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.user_id} {self.date} {self.created_at:%F %T}"