
from django.contrib import admin
from django.urls import path, re_path, include
from user.views import login_template ,logout_view
from django_prometheus import exports
from user.views import crash, slow

urlpatterns = [
    # 🔹 /metrics, /metrics/ 둘 다 받게끔 (가장 안전)
    re_path(r"^metrics/?$", exports.ExportToDjangoView, name="prometheus-django-metrics"),
    path('admin/', admin.site.urls),
    path("crash/", crash), 
    path("slow/", slow),
    path("api/diary/", include("diaryrewriting.urls")),
    path('', login_template),  # 로그인 템플릿
    path("api/coupang/", include("coupangapi.urls")),  
    path("api/user/", include("user.urls")),
    path("api/", include("payments.urls")),
    path("api/", include("summary.urls")),
    path("api/auth/logout/",logout_view) 

]
