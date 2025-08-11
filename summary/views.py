from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from openai import OpenAI
import json, re

# OpenAI 클라이언트 생성 (키는 settings.py에서 .env로 불러옴)
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def call_openai(entries):
    """
    entries: [{"text": "...", "emotion": "..."}, ...]
    -> GPT에 프롬프트로 보내서 요약 JSON 반환
    """
    # 프롬프트 구성
    lines = ["다음은 오늘 하루 동안의 감정 기록입니다:"]
    for e in entries:
        emo = e.get("emotion", "기타")
        txt = e.get("text", "")
        lines.append(f"- ({emo}) {txt}")
    lines.append("")
    lines.append("이 기록들을 바탕으로 오늘 하루의 감정을 요약하고, 대표 감정 하나와 추천 아이템 2개를 제안해주세요.")
    lines.append("결과는 아래 JSON 형식으로 주세요:")
    lines.append('{"summary_text":"...", "emotion":"...", "recommended_items":["...","..."]}')

    prompt = "\n".join(lines)

    # GPT 호출
    resp = client.chat.completions.create(
        model="gpt-4o-mini",  # 비용 적은 모델 (원하면 gpt-4o로 변경 가능)
        temperature=0.7,
        messages=[
            {"role": "system", "content": "너는 한국어로 정갈한 감정 요약을 작성하는 어시스턴트다."},
            {"role": "user", "content": prompt}
        ],
    )

    # 응답 텍스트 추출
    content = resp.choices[0].message.content

    # JSON만 추출
    json_str = re.search(r"\{.*\}", content, re.S)
    return json.loads(json_str.group(0)) if json_str else {"raw": content}

@api_view(["POST"])
def generate_summary(request):
    """
    POST /api/summary/generate/
    body: { "entries": [ {"text":"...", "emotion":"..."}, ... ] }
    """
    try:
        entries = request.data.get("entries", [])
        if not isinstance(entries, list) or not entries:
            return Response({"detail": "entries(list)가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        result = call_openai(entries)
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
