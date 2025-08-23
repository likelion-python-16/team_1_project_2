# services/hf_summarizer.py

import os
import re
from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

MODEL_SUM = os.getenv("HF_SUMMARY_MODEL", "gogamza/kobart-summarization")
INSTRUCTION_MODE = os.getenv("HF_SUMMARY_INSTRUCTION", "false").lower() == "true"

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


def _pick_task(model_name: str) -> str:
    name = model_name.lower()
    if "kobart" in name or "summarization" in name:
        return "summarization"
    if "t5" in name or "flan" in name or "alpaca" in name:
        return "text2text-generation"
    return "summarization"


@lru_cache(maxsize=1)
def _sum_pipe():
    task = _pick_task(MODEL_SUM)
    tok = AutoTokenizer.from_pretrained(MODEL_SUM)
    mdl = AutoModelForSeq2SeqLM.from_pretrained(MODEL_SUM)
    return pipeline(task, model=mdl, tokenizer=tok)


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


def _summarize_piece(gen, task: str, text: str, max_new_tokens: int):
    text = _clean_text(text)
    is_kobart = "kobart" in MODEL_SUM.lower()
    if task == "summarization":
        # KoBART 경로: 지시문 붙이지 않고 그대로 요약
        res = gen(
            text,
            max_length=max_new_tokens,
            min_length=max(20, max_new_tokens // 4),
            do_sample=False,
            **GEN_KW,
        )
    else:
        # Instruction 모델일 때만 지시문 허용
        if is_kobart or not INSTRUCTION_MODE:
            prompt = text
        else:
            prompt = f"다음 내용을 한국어로 2~4문장으로 요약하라:\n{text}"
        res = gen(prompt, max_new_tokens=max_new_tokens, do_sample=False, **GEN_KW)

    return (res[0].get("summary_text") or res[0].get("generated_text") or "").strip()


def _safe_call(gen, task, text, max_new_tokens):
    try:
        out = _summarize_piece(gen, task, text, max_new_tokens)
        return _clean_text(out)
    except Exception:
        return ""


def summarize_korean(text: str, max_new_tokens: int = 160) -> str:
    """긴 입력 안정 처리 + KoBART 프롬프트 제거 + 계층형 폴백"""
    if not text or not text.strip():
        return ""
    gen = _sum_pipe()
    task = _pick_task(MODEL_SUM)
    is_kobart = "kobart" in MODEL_SUM.lower()

    # 1) 길면 chunk로 1차 요약
    chunks = _chunk_text(text)
    partials = []
    for c in chunks:
        s = _safe_call(gen, task, c, max_new_tokens=max_new_tokens // 2)
        if not s:
            s = _clean_text(c[:300])
        partials.append(s)

    if len(partials) == 1:
        return partials[0].strip()

    # 2) 1차 요약 합쳐 메타 요약
    joined = "\n".join(f"- {p}" for p in partials)

    # KoBART는 메타 단계도 지시문 금지
    if is_kobart:
        meta_in = joined
    else:
        meta_in = (
            f"다음 개요를 2~3문단 한국어로 자연스럽게 요약하라. "
            f"감정 흐름을 드러내고 중복을 제거하라:\n{joined}"
            if INSTRUCTION_MODE else joined
        )

    meta = _safe_call(gen, task, meta_in, max_new_tokens=max_new_tokens)
    if not meta:
        meta = _clean_text(" ".join(partials)[:600])
    return meta