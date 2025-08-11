def build_prompt(entries):
    prompt = "다음은 오늘 하루 동안의 감정 기록입니다:\n"
    for entry in entries:
        prompt += f"- ({entry['emotion']}) {entry['text']}\n"
    prompt += "\n이 기록들을 바탕으로 하루 감정을 요약하고, 대표 감정과 추천 아이템 2개를 제안해주세요.\n"
    prompt += '''JSON 형식:
{
  "summary_text": "...",
  "emotion": "...",
  "recommended_items": ["...", "..."]
}
'''
    return prompt
