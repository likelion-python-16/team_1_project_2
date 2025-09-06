# coupangapi/services/link_builder.py
from typing import List, Dict
from urllib.parse import quote_plus

# 기본 검색 엔진(원하는 것만 남기거나 추가하세요)
ENGINES = [
    {
        "name": "Coupang",
        "build": lambda q: f"https://www.coupang.com/np/search?q={quote_plus(q)}",
    },
    
]


def build_links_for_keyword(keyword: str, engines: List[Dict] = ENGINES) -> List[Dict]:
    """키워드로 각 엔진의 검색 링크를 만든다."""
    if not keyword or not keyword.strip():
        return []
    out: List[Dict] = []
    for e in engines:
        out.append({
            "title": f"{keyword}",
            "link": e["build"](keyword),
            "source": e["name"],
            "keyword": keyword,
        })
    return out