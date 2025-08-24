# services/hf_summarizer.py
import os
import re
from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

# ✔ 요약 전용 모델만 쓰세요 (예: gogamza/kobart-summarization, lcw99/t5-base-korean-text-summary 등)
MODEL_SUM = os.getenv("HF_SUMMARY_MODEL", "gogamza/kobart-summarization")

# 입력 길이 초과 대비
MAX_INPUT_TOKENS = int(os.getenv("HF_SUMMARY_MAX_INPUT_TOKENS", "900"))
CHUNK_OVERLAP = int(os.getenv("HF_SUMMARY_CHUNK_OVERLAP", "50"))

# 생성 옵션(반복 억제)
GEN_KW = {
    "num_beams": 4,
    "no_repeat_ngram_size": 4,
    "repetition_penalty": 1.8,
    "early_stopping": True,
}

def _clean_text(s: str) -> str:
    """대괄호/과한 특수문자/연속 공백 정리 (반복 완화)"""
    if not s:
        return ""
    s = s.replace("[", "(").replace("]", ")")
    s = re.sub(r"[^\S\r\n]+", " ", s)  # 다중 공백 → 단일 공백
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

@lru_cache(maxsize=1)
def _sum_pipe():
    # ✅ 무조건 요약 파이프라인 사용
    tok = AutoTokenizer.from_pretrained(MODEL_SUM)
    mdl = AutoModelForSeq2SeqLM.from_pretrained(MODEL_SUM)
    return pipeline("summarization", model=mdl, tokenizer=tok)

def _chunk_text(text: str):
    tok = _sum_pipe().tokenizer
    ids = tok.encode(text, add_special_tokens=False)
    n = len(ids)
    if n <= MAX_INPUT_TOKENS:
        return [text]
    chunks, start = [], 0
    while start < n:
        end = min(n, start + MAX_INPUT_TOKENS)
        piece = tok.decode(ids[start:end], skip_special_tokens=True)
        chunks.append(piece)
        if end == n:
            break
        start = max(0, end - CHUNK_OVERLAP)
    return chunks

def _summarize_piece(gen, text: str, max_new_tokens: int):
    text = _clean_text(text)
    # summarization 파이프라인은 보통 summary_text 키를 반환
    res = gen(
        text,
        max_length=max_new_tokens,
        min_length=max(20, max_new_tokens // 4),
        do_sample=False,
        **GEN_KW,
    )
    return (res[0].get("summary_text") or res[0].get("generated_text") or "").strip()

def _safe_call(gen, text, max_new_tokens):
    try:
        out = _summarize_piece(gen, text, max_new_tokens)
        return _clean_text(out)
    except Exception:
        return ""

def summarize_korean(text: str, max_new_tokens: int = 160) -> str:
    """
    순수 요약 전용: 입력 텍스트만 요약.
    - 길면 chunk 요약 → 2차 메타 요약(지시문 없이)
    """
    if not text or not text.strip():
        return ""
    gen = _sum_pipe()

    # 1) 길면 chunk로 1차 요약
    chunks = _chunk_text(text)
    partials = []
    half = max(40, max_new_tokens // 2)  # 1차 요약은 조금 짧게
    for c in chunks:
        s = _safe_call(gen, c, max_new_tokens=half)
        if not s:
            s = _clean_text(c[:300])
        partials.append(s)

    if len(partials) == 1:
        return partials[0].strip()

    # 2) 1차 요약들을 합쳐 최종 요약(지시문 없이 그대로 요약)
    joined = "\n".join(f"- {p}" for p in partials)
    final = _safe_call(gen, joined, max_new_tokens=max_new_tokens)
    if not final:
        final = _clean_text(" ".join(partials)[:600])
    return final