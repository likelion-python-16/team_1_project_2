
import uuid
from django.db import models

class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

class DiaryEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="entries")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    emotion = models.CharField(max_length=50, null=True, blank=True)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

class DailySummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="summaries")
    date = models.DateField()
    summary_text = models.TextField()
    emotion = models.CharField(max_length=50)
    recommended_items = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "date")
        ordering = ["-date"]
