from collections import defaultdict

def pick_overall_emotion(preds):
  # preds: [{'label': str, 'score': float}, ...]
  if not preds: return ""
  sums = defaultdict(float)
  for p in preds:
    lab = p.get("label")
    sc = float(p.get("score", 0.0))
    if lab: sums[lab] += sc
  return max(sums, key=sums.get) if sums else ""