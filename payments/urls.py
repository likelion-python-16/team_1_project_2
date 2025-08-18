from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from . import views

urlpatterns = [
    # === API ===
    # path("api/register/", views.RegisterView.as_view(), name="api-register"),  # 실제 POST 회원가입
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/me/", views.UserDetailView.as_view(), name="user-detail"),
    path("api/verify-payment/", views.VerifyPaymentView.as_view(), name="verify-payment"),

    # === HTML 페이지 ===
    # path("register/", views.register_page, name="register-page"),       # GET /register/ -> HTML
    # path("login/", views.login_page, name="login-page"),                # GET /login/ -> HTML
    path("payment-page/", views.payment_page, name="payment-page"),
    path("toss/success/", views.success_page, name="toss-success"),
    path("toss/fail/", views.fail_page, name="toss-fail"),
]