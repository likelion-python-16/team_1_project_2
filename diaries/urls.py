from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiaryEntryViewSet, DiaryEntryCreateView

router = DefaultRouter()
router.register(r'diaries', DiaryEntryViewSet, basename='diary')

urlpatterns = [
    path('', include(router.urls)),
    path('diaries/create/', DiaryEntryCreateView.as_view(), name='diary-create'),
]
