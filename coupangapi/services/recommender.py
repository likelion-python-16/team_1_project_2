# coupangapi/services/recommender.py
from typing import List

EMOTION_KEYWORDS = {
    "행복": ["간식 선물", "케이크", "콜드브루 원두"],
    "슬픔": ["다크 초콜릿", "캐모마일 티", "힐링 음악", "무드등"],
    "분노": ["스트레스볼", "폼롤러", "러닝화", "펀치백 쿠션"],
    "불안": ["아로마 캔들", "명상 앱 이용권", "수면 안대", "허브티"],
    "놀람": ["폴라로이드 필름", "포토카드 앨범", "엽서 세트"],
    "혐오": ["섬유 탈취제", "핸드워시", "공기정화 식물"],
    "공포": ["무드등", "담요", "허브티"],
    "중립": ["노트", "볼펜 세트", "이어폰", "북마크"],
}

def keywords_for_emotion(emotion: str) -> List[str]:
    return EMOTION_KEYWORDS.get(emotion or "중립", EMOTION_KEYWORDS["중립"])