from rest_framework.routers import DefaultRouter
from .views import DailySummaryViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'', DailySummaryViewSet, basename='daily-summary')

urlpatterns = [
    path('', include(router.urls)),
]
