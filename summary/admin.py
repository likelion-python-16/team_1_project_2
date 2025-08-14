from django.contrib import admin
from .models import EmotionDiary, DiaryRecord


@admin.register(EmotionDiary)
class EmotionDiaryAdmin(admin.ModelAdmin):
    list_display = ("date", "content", "emotions")
    search_fields = ("content",)
    list_filter = ("date",)


@admin.register(DiaryRecord)
class DiaryRecordAdmin(admin.ModelAdmin):
    list_display = ("time", "text")
    search_fields = ("text",)
    list_filter = ("time",)
