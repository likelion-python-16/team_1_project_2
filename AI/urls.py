
from django.contrib import admin
from django.urls import path, include
from user.views import login_template, profile_template, kakao_callback, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/diary/", include("diaryrewriting.urls")),
    path('', login_template),  # 로그인 템플릿
    path('profile/', profile_template),  # 프로필 템플릿
    path('user/login/callback/', kakao_callback),  # 카카오 redirect 콜백
    path('logout/', logout_view),
    path("", include("payments.urls")),
    path("", include("summary.urls")),
]
