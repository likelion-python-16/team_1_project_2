# settings.py
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# --- 필수 비밀키 확인 ---
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing. Check your .env")

DEBUG = True

# 개발 편의: 외부 접근 허용
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # third-party
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    # local apps
    "diaryrewriting",
    "user",
    "summary",
    "payments",
    "coupangapi",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",   # ✅ CORS는 최대한 위쪽
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # ❌ 중복 제거: SessionMiddleware 두 번 금지
]

ROOT_URLCONF = "AI.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "AI.wsgi.application"

# --- DB ---
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.getenv("DB_NAME","project2_db"),
        "USER": os.getenv("DB_USER","prject2_user"),
        "PASSWORD": os.getenv("DB_PASSWORD","DjangoUserPass!123"),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            # ✅ 문자셋 + 타임존 고정 (UTC) – 타임존 이슈 예방
            "init_command": "SET time_zone = '+09:00'",
        },
    }
}
if os.environ.get("TEST"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Use Amazon
if os.environ.get("S3_BUCKET"):
    STORAGES = {
        "default": {
             "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": os.environ.get("S3_BUCKET"),
                "region_name": os.environ.get("S3_REGION", "ap-northeast-2"),
                "custom_domain": os.environ.get("S3_CUSTOM_DOMAIN"),
                "location": "media",
                "default_acl": "public-read",
                "querystring_auth": False,
            },
        },
        "staticfiles": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "bucket_name": os.environ.get("S3_BUCKET"),
                "region_name": os.environ.get("S3_REGION", "ap-northeast-2"),
                "custom_domain": os.environ.get("S3_CUSTOM_DOMAIN"),
                "location": "static",
                "default_acl": "public-read",
                "querystring_auth": False,
            },
        },
    }



AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ko-kr"
TIME_ZONE = "Asia/Seoul"
USE_I18N = True
USE_TZ = True  # ✅ DB에는 UTC 저장, 애플리케이션에서 변환

# --- Static ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- CORS ---
CORS_ALLOW_ALL_ORIGINS = True          # 개발용
# CORS_ALLOW_CREDENTIALS = True        # 쿠키/세션을 쓸 경우 활성화
# 배포 시:
# CORS_ALLOWED_ORIGINS = ["https://your-frontend.example.com"]
# CSRF_TRUSTED_ORIGINS = ["https://your-frontend.example.com"]

# --- REST/JWT ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # 필요하면 여기에서 전역 페이지네이션 끄거나 조절:
    # "DEFAULT_PAGINATION_CLASS": None,
    # "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# --- OAuth/결제 (민감정보는 .env로 이동 권장) ---
KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY", "")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "http://localhost:8000/api/user/login/callback/")
TOSS_SECRET_KEY = os.getenv("TOSS_SECRET_KEY", "")
TOSS_CLIENT_KEY = os.getenv("TOSS_CLIENT_KEY", "")
SESSION_ENGINE = "django.contrib.sessions.backends.db"