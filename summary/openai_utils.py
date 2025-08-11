# gpt_summary/openai_utils.py
from openai import OpenAI
from django.conf import settings
from .prompts import build_prompt

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_daily_summary(entries):
    prompt = build_prompt(entries)
    resp = client.chat.completions.create(
        model="gpt-4o",  # 또는 "gpt-4o-mini" 원하면
        messages=[
            {"role": "system", "content": "감정 기반 요약 도우미입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
    )
    return resp.choices[0].message.content
