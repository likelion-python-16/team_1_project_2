from django.urls import path
from . import views

urlpatterns = [
    path('login/kakao/', views.kakao_login_url),
    path('login/callback/', views.kakao_callback),
    path('profile/', views.profile),
]
