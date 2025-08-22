# diaryrewriting/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("whoami/", views.whoami),
    path("entries/", views.list_entries),
    path("entries/create/", views.create_entry),
    path("days/", views.list_days),

    # 요약 생성/조회
    path("finalize-summary/", views.finalize_day_summary),
    path("summaries/", views.get_summary),  # GET ?date=YYYY-MM-DD
]