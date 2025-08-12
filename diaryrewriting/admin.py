
from django.contrib import admin
from .models import User, DiaryEntry, DailySummary

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at")
    search_fields = ("id",)

@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "timestamp", "emotion")
    list_filter = ("emotion",)
    search_fields = ("content",)

@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "date", "emotion")
    list_filter = ("emotion", "date")
    search_fields = ("summary_text", "diary_text")
