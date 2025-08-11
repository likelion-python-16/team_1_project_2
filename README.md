
# Summary (One-line Diary) – Drop-in Django App

This folder contains a reusable Django app `summary` providing APIs to store one-line diary entries and generate a daily emotional summary using OpenAI.

## Install (drop-in)

1) Copy the `summary` folder into your Django project root (next to your project package).
2) Install deps:
   ```bash
   pip install -r requirements.txt
   ```
3) Add to settings.py:
   ```python
   INSTALLED_APPS += ["rest_framework", "corsheaders", "summary"]
   MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"] + MIDDLEWARE
   CORS_ALLOW_ALL_ORIGINS = True  # for dev
   # Load .env if you want:
   from pathlib import Path
   import os
   from dotenv import load_dotenv
   load_dotenv(os.path.join(BASE_DIR, ".env"))
   ```
4) Wire URLs (project urls.py):
   ```python
   from django.urls import path, include
   urlpatterns = [
       # ...
       path("api/summary/", include("summary.urls")),
   ]
   ```
5) Migrate:
   ```bash
   python manage.py migrate
   ```

## .env
Copy `.env.example` to `.env` and set your `OPENAI_API_KEY`. Optionally override `OPENAI_MODEL`.

## API (quick)

- `GET  /api/summary/whoami/` → returns a UUID user, also sets `uid` cookie
- `POST /api/summary/entries/create/` with JSON `{content, emotion?, lat?, lng?}`
- `GET  /api/summary/entries/?date=YYYY-MM-DD` → list entries for a day (or all if omitted)
- `GET  /api/summary/days/` → list days with counts
- `POST /api/summary/generate/` with JSON `{date?: YYYY-MM-DD}` → create/update summary for that date
- `GET  /api/summary/summaries/?date=YYYY-MM-DD` → get stored summary

Client can also pass `X-User-Id: <uuid>` header to control the user identity. Otherwise a new UUID is created and set via `uid` cookie.

## Notes
- The OpenAI call is minimal and robust to slightly messy JSON by best-effort parsing.
- You can swap the model via env var `OPENAI_MODEL`.
- For prod, tighten CORS and add auth as needed.
