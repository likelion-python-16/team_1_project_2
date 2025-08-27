from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import os

MODEL_EMO = os.getenv("HF_EMOTION_MODEL", "Jinuuuu/KoELECTRA_fine_tunning_emotion")

@lru_cache(maxsize=1)
def _emo_pipe():
  tok = AutoTokenizer.from_pretrained(MODEL_EMO)
  mdl = AutoModelForSequenceClassification.from_pretrained(MODEL_EMO)
  return pipeline("text-classification", model=mdl, tokenizer=tok)  # GPU 있으면 device=0

def predict_emotions(texts):
  if not texts: return []
  clf = _emo_pipe()
  out = clf(texts, truncation=True)
  return out if isinstance(out, list) else [out]