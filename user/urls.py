from django.urls import path
from . import views

urlpatterns = [
    
    path('login/callback/', views.kakao_callback),
    path('profile/', views.profile_template),
    path('logout/', views.logout_view),
]
