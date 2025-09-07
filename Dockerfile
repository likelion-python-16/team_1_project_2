FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# 필수 빌드 의존성 (mysqlclient 빌드용 헤더 포함)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      default-libmysqlclient-dev \
      pkg-config \
 # 디스크 아끼기
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 요구사항만 먼저 복사해서 캐시 레이어 최대 활용
COPY requirements.prod.txt /app/

# 1) CPU 전용 PyTorch 설치 (CUDA 아님!)
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu \
      torch==2.3.1+cpu

# 2) 나머지 파이썬 의존성 설치
RUN pip install --no-cache-dir -r requirements.prod.txt \
 && pip install --no-cache-dir gunicorn

# 앱 소스 복사
COPY . /app

# gunicorn 실행(예: 장고)
CMD ["gunicorn", "AI.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]