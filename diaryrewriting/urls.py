# diaryrewriting/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 유저/엔트리
    path("whoami/", views.whoami, name="whoami"),
    path("entries/", views.list_entries, name="entry-list"),           # GET (date=YYYY-MM-DD)
    path("entries/create/", views.create_entry, name="entry-create"),  # POST
    path("entries/<int:pk>/", views.retrieve_entry, name="entry-detail"),     # GET
    path("entries/<int:pk>/update/", views.update_entry, name="entry-update"),# PUT/PATCH
    path("entries/<int:pk>/delete/", views.delete_entry, name="entry-delete"),# DELETE
    path("days/", views.list_days, name="days"),

    # 요약
    path("finalize-summary/", views.finalize_day_summary, name="finalize-summary"),  # POST
    path("summaries/", views.get_summary, name="summary-get"),                       # GET (date=YYYY-MM-DD)
]