from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiaryEntryViewSet, DiaryEntryCreateView

router = DefaultRouter()
router.register(r'', DiaryEntryViewSet, basename='diary')

urlpatterns = [
    path('', include(router.urls)),
    path('entries/', DiaryEntryCreateView.as_view(), name='diary-entry-create'),
]
