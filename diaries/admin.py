from django.contrib import admin
from .models import DiaryEntry

@admin.register(DiaryEntry)
class DiaryEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'text', 'emotion', 'created_at']
    readonly_fields = ['id', 'created_at']
