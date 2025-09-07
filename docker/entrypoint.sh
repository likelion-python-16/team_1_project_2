#!/usr/bin/env bash
set -e

# Health check: DB 준비될 때까지 대기 (선택)
if [ -n "${DB_HOST}" ]; then
  echo "⏳ Waiting for DB at ${DB_HOST}:${DB_PORT:-3306} ..."
  ATTEMPTS=0
  until nc -z "${DB_HOST}" "${DB_PORT:-3306}" || [ $ATTEMPTS -ge 30 ]; do
    ATTEMPTS=$((ATTEMPTS+1))
    sleep 1
  done
fi

# Django 초기화
echo "🚀 Running migrations..."
python manage.py migrate --noinput

# collectstatic (STATIC_ROOT 설정되어 있으면 동작)
echo "🧹 Collect static..."
python manage.py collectstatic --noinput || true

# 모드별 실행
if [ "${DJANGO_ENV}" = "dev" ]; then
  echo "🌱 Starting Django dev server..."
  exec python manage.py runserver 0.0.0.0:8000
else
  echo "🦄 Starting Gunicorn..."
  exec gunicorn AI.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
fi