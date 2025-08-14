
# diaryrewriting – Drop-in Django App (Ghostwritten Daily Diary)

Reusable Django app `diaryrewriting` that stores one-line entries and generates a ghostwritten daily diary using OpenAI.

## Install

1) Copy the `diaryrewriting/` folder into your Django project root.
2) Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3) Update settings.py:
   ```python
   INSTALLED_APPS += ["rest_framework", "corsheaders", "diaryrewriting"]
   MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"] + MIDDLEWARE
   CORS_ALLOW_ALL_ORIGINS = True  # dev only
   # load .env (optional)
   from dotenv import load_dotenv
   import os
   load_dotenv(os.path.join(BASE_DIR, ".env"))
   ```
4) Wire URLs (project urls.py):
   ```python
   from django.urls import path, include
   urlpatterns = [
       # ...
       path("api/diary/", include("diaryrewriting.urls")),
   ]
   ```
5) Migrate:
   ```bash
   python manage.py migrate
   ```

## API

- `GET  /api/diary/whoami/`
- `POST /api/diary/entries/create/`  `{content, emotion?, lat?, lng?}`
- `GET  /api/diary/entries/?date=YYYY-MM-DD`
- `GET  /api/diary/days/`
- `POST /api/diary/generate/` or `/api/diary/generate_diary/` `{date?: YYYY-MM-DD}`
- `GET  /api/diary/summaries/?date=YYYY-MM-DD`
- `GET  /api/diary/diaries/?date=YYYY-MM-DD`  → returns only `{date, diary_text}`

Client can pass `X-User-Id: <uuid>` header to fix identity, or rely on the `uid` cookie set by responses.

## Notes
- Model `DailySummary` includes `diary_text` (main ghostwritten diary), plus short `summary_text` and `emotion`.
- OpenAI model defaults to `gpt-4o-mini` (override via `OPENAI_MODEL`).
- Harden CORS/auth before production.


API 문서

| Group                   | Method | URL                   | Request Body (JSON example)                                                                                                                                                                      | Success Response (JSON example)                                                                                                                                                                                                                   | Auth    | Description                                |
|-------------------------|--------|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------|--------------------------------------------|
| Auth                    | POST   | /api/token/           | `{ "username": "test_user", "password": "test_password" }`                                                                                                                                       | `{ "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }`                                                                                                                                     | None    | JWT 발급(Access/Refresh)                   |
| User                    | GET    | /api/me/              |                                                                                                                                                                                                   | `{ "username": "test_user" }`                                                                                                                                                                                                                     | Bearer  | 현재 로그인 사용자 이름 조회               |
| Payments                | POST   | /api/verify-payment/  | `{ "paymentKey": "pay_20250814_0001" }`                                                                                                                                                          | `{ "detail": "검증 성공", "status": "DONE" }`                                                                                                                                                                                                     | Bearer  | Toss 결제 상태 검증                         |
| Summary-EmotionDiary    | GET    | /diary/               |                                                                                                                                                                                                   | `[ { "id": 1, "date": "2025-08-13", "content": "오늘은 팀 프로젝트 회의를 했다.", "emotions": { "dominant": "joy", "scores": { "joy": 0.82, "sad": 0.05, "neutral": 0.13 } } }, { "id": 2, "date": "2025-08-14", "content": "비가 왔지만 개발이 잘 풀렸다.", "emotions": { "dominant": "calm", "scores": { "joy": 0.55, "calm": 0.7, "anger": 0.02 } } } ]` | Depends on DRF defaults | EmotionDiary 목록 (-date 정렬은 모델에 없음) |
| Summary-EmotionDiary    | POST   | /diary/               | `{ "date": "2025-08-15", "content": "리팩토링으로 응답 속도가 개선됨.", "emotions": { "dominant": "satisfied", "scores": { "satisfied": 0.66, "neutral": 0.3 } } }`                                 | `{ "id": 3, "date": "2025-08-15", "content": "리팩토링으로 응답 속도가 개선됨.", "emotions": { "dominant": "satisfied", "scores": { "satisfied": 0.66, "neutral": 0.3 } } }`                                                                       | Depends on DRF defaults | EmotionDiary 생성                           |
| Summary-EmotionDiary    | GET    | /diary/{id}/          |                                                                                                                                                                                                   | `{ "id": 1, "date": "2025-08-13", "content": "오늘은 팀 프로젝트 회의를 했다.", "emotions": { "dominant": "joy", "scores": { "joy": 0.82, "sad": 0.05, "neutral": 0.13 } } }`                                                                     | Depends on DRF defaults | EmotionDiary 상세                           |
| Summary-EmotionDiary    | PUT    | /diary/{id}/          | `{ "date": "2025-08-13", "content": "회의 내용을 정리하여 기록(전체 수정).", "emotions": { "dominant": "focused", "scores": { "focused": 0.74, "neutral": 0.2 } } }`                               | `{ "id": 1, "date": "2025-08-13", "content": "회의 내용을 정리하여 기록(전체 수정).", "emotions": { "dominant": "focused", "scores": { "focused": 0.74, "neutral": 0.2 } } }`                                                                     | Depends on DRF defaults | EmotionDiary 전체 수정                       |
| Summary-EmotionDiary    | PATCH  | /diary/{id}/          | `{ "emotions": { "dominant": "tired", "scores": { "tired": 0.51, "neutral": 0.49 } } }`                                                                                                           | `{ "id": 1, "date": "2025-08-13", "content": "오늘은 팀 프로젝트 회의를 했다.", "emotions": { "dominant": "tired", "scores": { "tired": 0.51, "neutral": 0.49 } } }`                                                                               | Depends on DRF defaults | EmotionDiary 부분 수정                       |
| Summary-EmotionDiary    | DELETE | /diary/{id}/          |                                                                                                                                                                                                   |                                                                                                                                                                                                                                                   | Depends on DRF defaults | EmotionDiary 삭제 (204)                      |
| Summary-DiaryRecord     | GET    | /record/              |                                                                                                                                                                                                   | `[ { "id": 10, "time": "09:30:00", "text": "아침 운동 20분 조깅" }, { "id": 11, "time": "14:00:00", "text": "DRF Router 구성" } ]`                                                                                                                   | Depends on DRF defaults | DiaryRecord 목록 (-time 정렬)                |
| Summary-DiaryRecord     | POST   | /record/              | `{ "time": "10:15:00", "text": "프로젝트 일정 점검 회의" }`                                                                                                                                      | `{ "id": 12, "time": "10:15:00", "text": "프로젝트 일정 점검 회의" }`                                                                                                                                                                              | Depends on DRF defaults | DiaryRecord 생성                             |
| Summary-DiaryRecord     | GET    | /record/{id}/         |                                                                                                                                                                                                   | `{ "id": 10, "time": "09:30:00", "text": "아침 운동 20분 조깅" }`                                                                                                                                                                                  | Depends on DRF defaults | DiaryRecord 상세                             |
| Summary-DiaryRecord     | PUT    | /record/{id}/         | `{ "time": "09:45:00", "text": "아침 운동 페이스 업(전체 수정)" }`                                                                                                                                | `{ "id": 10, "time": "09:45:00", "text": "아침 운동 페이스 업(전체 수정)" }`                                                                                                                                                                        | Depends on DRF defaults | DiaryRecord 전체 수정                         |
| Summary-DiaryRecord     | PATCH  | /record/{id}/         | `{ "text": "거리 3km 기록" }`                                                                                                                                                                    | `{ "id": 10, "time": "09:30:00", "text": "거리 3km 기록" }`                                                                                                                                                                                        | Depends on DRF defaults | DiaryRecord 부분 수정                         |
| Summary-DiaryRecord     | DELETE | /record/{id}/         |                                                                                                                                                                                                   |                                                                                                                                                                                                                                                   | Depends on DRF defaults | DiaryRecord 삭제 (204)                        |
