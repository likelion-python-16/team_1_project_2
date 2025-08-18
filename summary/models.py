from django.db import models

# Create your models here.
class EmotionDiary(models.Model):
    date = models.DateField()
    content = models.TextField()
    emotions = models.JSONField()
    def __str__(self):
        return f"{self.date} - {self.summary}"



class DiaryRecord(models.Model):

    time = models.TimeField()
    text = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.time} - {self.text}"