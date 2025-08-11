from django.urls import path
from .views import generate_summary

urlpatterns = [
    path('generate/', generate_summary, name='generate-summary'),
]
