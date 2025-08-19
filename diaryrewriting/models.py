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
    emotion = models.CharField(max_length=50, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]


class DailySummary(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="summaries"
    )
    date = models.DateField()
    summary_text = models.TextField(blank=True)
    emotion = models.CharField(max_length=50, blank=True)
    recommended_items = models.JSONField(null=True, blank=True)
    diary_text = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]
