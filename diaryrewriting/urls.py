
from django.urls import path
from . import views

urlpatterns = [
    path("whoami/", views.whoami),
    path("entries/", views.list_entries),
    path("entries/create/", views.create_entry),
    path("days/", views.list_days),
    path("finalize-summary/", views.finalize_day_summary),      # backward compatible
    path("summaries/", views.get_summary),
    path("generate_diary/", views.generate_diary),  # semantic alias
    path("diaries/", views.get_diary),
]
