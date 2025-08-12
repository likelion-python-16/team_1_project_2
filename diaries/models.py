import datetime
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from summaries.models import DailySummary

class DiaryEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()  # 일기 내용
    emotion = models.CharField(max_length=30, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 생성일시 자동 저장

    def __str__(self):
        return f"{self.user.email} - {self.created_at.date()}"


@receiver(post_save, sender=DiaryEntry)
def create_or_update_daily_summary(sender, instance, created, **kwargs):
    """일기 저장 시, 해당 날짜의 요약을 생성/업데이트"""
    if not created:
        return  # 새로 만든 경우만 처리

    today = instance.created_at.date()

    # 해당 유저 + 해당 날짜 요약이 이미 있으면 건너뜀
    if DailySummary.objects.filter(user=instance.user, date=today).exists():
        return

    # TODO: AI 감정 분석 & 요약 로직 추가 가능
    emotion = "기쁨"  # 예시 값
    summary = f"{today}의 첫 번째 일기 요약입니다."  # 요약 텍스트

    DailySummary.objects.create(
        user=instance.user,
        date=today,
        emotion=emotion,
        summary=summary
    )
