# diaryrewriting/services/emotion_aggregate.py
from typing import List, Dict
from collections import defaultdict

# 영문/변형 라벨 → 한국어 표준 라벨
_ALIAS_TO_KO = {
    # 행복 계열
    "joy": "행복", "happiness": "행복", "happy": "행복", "pleasure": "행복", "love": "행복",
    # 슬픔
    "sad": "슬픔", "sadness": "슬픔", "sorrow": "슬픔",
    # 분노
    "anger": "분노", "angry": "분노", "rage": "분노",
    # 공포/불안
    "fear": "공포", "scared": "공포",
    "anxiety": "불안", "anxious": "불안",
    # 혐오
    "disgust": "혐오", "disgusted": "혐오",
    # 놀람
    "surprise": "놀람", "surprised": "놀람",
    # 중립/기타
    "neutral": "중립", "none": "중립", "other": "중립", "others": "중립",
}

# 한국어 입력도 표준화 (안전망)
_KO_CANONICAL = {k: k for k in ["행복","슬픔","분노","공포","불안","혐오","놀람","중립"]}

def normalize_emotion(label: str) -> str:
    """영문/변형/한글 혼재 라벨을 한국어 표준 라벨로 정규화."""
    if not label:
        return "중립"
    s = str(label).strip()
    if s in _KO_CANONICAL:
        return s
    return _ALIAS_TO_KO.get(s.lower(), "중립")

def pick_overall_emotion(preds: List[Dict]) -> str:
    """
    preds 예: [{'label': 'joy', 'score': 0.93}, ...] (영문/한글 혼재 가능)
    라벨을 정규화(한국어)한 뒤 score 합산으로 대표 감정 선택.
    """
    if not preds:
        return "중립"

    bucket = defaultdict(float)
    for p in preds:
        ko = normalize_emotion(p.get("label", ""))
        score = float(p.get("score", 0.0) or 0.0)
        bucket[ko] += score

    return max(bucket.items(), key=lambda x: x[1])[0]