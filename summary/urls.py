from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import HttpResponse
from .views import EmotionDiaryViewSet, DiaryRecordViewSet, summary_page

# 임시 list 페이지
def diary_list_page(request):
    return HttpResponse("<h1>여기는 임시 목록 페이지입니다.</h1>")

# API 라우터
router = DefaultRouter()
router.register(r'diary', EmotionDiaryViewSet)
router.register(r'record', DiaryRecordViewSet)

# API 라우트
api_urlpatterns = [
    path('', include(router.urls)),  # /api/summary/diary/, /api/summary/record/
]

# 페이지 라우트
page_urlpatterns = [
    path('list/', diary_list_page, name='diary-list'),
    path('summary_detail/', summary_page, name='summary-page'),
]

urlpatterns = api_urlpatterns + page_urlpatterns
