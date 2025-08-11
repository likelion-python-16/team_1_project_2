
import os
from datetime import date
from typing import List, Dict, Any, Tuple

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SYSTEM_PROMPT = (
    "You are an assistant that reads a user's one-line diary entries for a single day "
    "and produces: (1) a concise emotional summary in Korean (2-4 sentences), "
    "(2) a single representative emotion word, and (3) up to two friendly product or content suggestions "
    "relevant to that emotion. Return JSON with keys: summary_text, emotion, recommended_items (list of {title, reason}). "
    "Keep it supportive, never judgmental."
)

def summarize(entries: List[str], d: date) -> Tuple[str, str, list]:
    if not OpenAI:
        # Fallback if SDK isn't installed at import time (unit tests, etc.)
        return ("요약을 생성할 수 없습니다(라이브러리 누락).", "unknown", [])
    if not OPENAI_API_KEY:
        return ("요약을 생성할 수 없습니다(API 키 누락).", "unknown", [])
    client = OpenAI(api_key=OPENAI_API_KEY)
    content = "\n".join(f"- {e}" for e in entries) or "(no entries)"
    prompt = f"Date: {d.isoformat()}\nEntries:\n{content}\n---\nProduce JSON per instructions."
    resp = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
    )
    text = resp.choices[0].message.content.strip()
    # Best effort JSON parse
    import json, re
    try:
        json_text = re.search(r"\{[\s\S]*\}", text).group(0)
        data = json.loads(json_text)
        summary_text = str(data.get("summary_text", "")).strip()
        emotion = str(data.get("emotion", "")).strip()
        recommended_items = data.get("recommended_items", []) or []
        # Normalize items
        norm = []
        for it in recommended_items:
            title = (it.get("title") if isinstance(it, dict) else str(it)) or ""
            reason = (it.get("reason") if isinstance(it, dict) else "") or ""
            if title:
                norm.append({"title": title, "reason": reason})
        return summary_text, emotion, norm[:2]
    except Exception:
        return text, "unknown", []
