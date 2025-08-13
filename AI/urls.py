
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/diary/", include("diaryrewriting.urls")),
    path("", include("payments.urls")),  # /payment-page/, /toss/success/ 등
    path("", RedirectView.as_view(url="/payment-page/", permanent=False)), # 루트 → 결제 페이지
]
