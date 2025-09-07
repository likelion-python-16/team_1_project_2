# ===== Runtime base =====
FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Asia/Seoul 타임존 고정 (로그/스케줄 정합)
    TZ=Asia/Seoul

WORKDIR /app

# 빌드/런타임 공통 패키지 (mysqlclient 빌드용)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# 요구사항 먼저 복사 → 캐시 최대활용
COPY requirements.txt /app/requirements.txt

# gunicorn은 배포에서 사용 (requirements.txt에 없으면 여기서 설치)
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# 앱 소스 복사
COPY . /app

# 실행 스크립트 복사 & 권한
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# DJANGO_ENV=dev|prod 로 모드 제어
ENV DJANGO_ENV=prod

CMD ["/entrypoint.sh"]