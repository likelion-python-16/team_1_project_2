from django.db import models
from django.conf import settings

class DailySummary(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    summary_text = models.TextField()
    emotion = models.CharField(max_length=50)
    recommended_items = models.JSONField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'date')
