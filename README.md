# 1. JWT 인증 방식 추가 (예: djangorestframework-simplejwt 설치 필요)
# 'DEFAULT_AUTHENTICATION_CLASSES'에 아래 추가:
# 'rest_framework_simplejwt.authentication.JWTAuthentication',

# 2. allauth 또는 social-auth-app-django 등을 통해 Google/Kakao OAuth 연동
# 'dj-rest-auth', 'allauth', 'social-auth-app-django' 등의 패키지를 사용하게 됨

# 예시 패키지 설치 (나중에)
# pip install dj-rest-auth[with_social] django-allauth

# 그 외:
# - LOGIN_REDIRECT_URL, SOCIALACCOUNT_PROVIDERS 등의 설정 추가
# - 인증 URL 라우팅 추가
