
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
