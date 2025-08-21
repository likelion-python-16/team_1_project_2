from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import os

MODEL_SUM = os.getenv("HF_SUMMARY_MODEL", "gogamza/kobart-summarization")  # 한국어 요약

@lru_cache(maxsize=1)
def _sum_pipe():
  tok = AutoTokenizer.from_pretrained(MODEL_SUM)
  mdl = AutoModelForSeq2SeqLM.from_pretrained(MODEL_SUM)
  return pipeline("text2text-generation", model=mdl, tokenizer=tok)

def summarize_korean(text, max_new_tokens=160):
  if not text or not text.strip():
    return ""
  gen = _sum_pipe()
  out = gen(text, max_new_tokens=max_new_tokens, do_sample=False)
  return out[0]["generated_text"].strip()