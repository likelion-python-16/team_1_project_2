# coupangapi/urls.py
from django.urls import path
from .views import create_or_refresh_recommendation, get_recommendation

urlpatterns = [
    path("recommendations/", create_or_refresh_recommendation, name="cp_create_or_refresh"),
    path("recommendations/detail/", get_recommendation, name="cp_get"),
]