
from django.contrib import admin
from django.urls import path, include
from user.views import login_template ,logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/diary/", include("diaryrewriting.urls")),
    path('', login_template),  # 로그인 템플릿
    path("api/coupang/", include("coupangapi.urls")),  
    path("api/user/", include("user.urls")),
    path("api/", include("payments.urls")),
    path("api/", include("summary.urls")),
    path("api/auth/logout/",logout_view)

]
