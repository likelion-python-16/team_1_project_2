
import os
from datetime import date
from typing import List, Tuple

try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

SYSTEM_PROMPT = (
    "You are a Korean diary ghostwriter. The user wrote many short SNS-like notes during the day. "
    "Write a single cohesive daily diary entry in Korean that sounds like the same person, "
    "gentle and honest but not cheesy. Keep concrete details and weave them into a flowing narrative "
    "(6~12 sentences). After the diary, also provide: "
    "(1) summary_text (1-2 sentences), "
    "(2) emotion (one word), "
    "(3) recommended_items (up to two, each {title, reason}). "
    "Return STRICT JSON with keys: diary_text, summary_text, emotion, recommended_items."
)

def summarize(entries: List[str], d: date) -> Tuple[str, str, list, str]:
    if not OpenAI:
        return ("", "unknown", [], "")
    if not OPENAI_API_KEY:
        return ("", "unknown", [], "")
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
    import json, re
    try:
        json_text = re.search(r"\{[\s\S]*\}", text).group(0)  # extract first JSON object
        data = json.loads(json_text)
        diary_text = str(data.get("diary_text", "")).strip()
        summary_text = str(data.get("summary_text", "")).strip()
        emotion = str(data.get("emotion", "")).strip()
        items = data.get("recommended_items", []) or []
        norm = []
        for it in items:
            if isinstance(it, dict):
                title = str(it.get("title", "")).strip()
                reason = str(it.get("reason", "")).strip()
            else:
                title = str(it).strip()
                reason = ""
            if title:
                norm.append({"title": title, "reason": reason})
        return summary_text, emotion, norm[:2], diary_text
    except Exception:
        return (text, "unknown", [], "")
