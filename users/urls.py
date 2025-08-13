from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from .views import RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view()),      # 회원가입
    path("token/", TokenObtainPairView.as_view()),  # 로그인(JWT)
]