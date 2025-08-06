from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="One-line Diary API",
      default_version='v1',
      description="AI 감정 기반 한줄일기 API 문서",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes=[], # swagger에서 인증 헤더를 넣을수 있도록 설정
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # 인증 URL (DRF 기본 로그인/로그아웃 뷰)
    path('api-auth/', include('rest_framework.urls')),

    # 앱별 API URL
    path('api/users/', include('users.urls')),
    path('api/diaries/', include('diaries.urls')),
    path('api/summaries/', include('summaries.urls')),

    # Swagger UI 문서
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
