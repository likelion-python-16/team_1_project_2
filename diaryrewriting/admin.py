# diaryrewriting/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import DiaryEntry, DailySummary

User = get_user_model()

@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "emotion", "timestamp")
    search_fields = ("content", "emotion")
    list_filter = ("emotion", "timestamp")
    raw_id_fields = ("user",)  # admin에서 user 선택 성능 개선

@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "emotion")
    search_fields = ("summary_text", "diary_text", "emotion")
    list_filter = ("date", "emotion")
    raw_id_fields = ("user",)