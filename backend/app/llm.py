from __future__ import annotations

import os
from typing import Any

from openai import OpenAI


def _rule_based(article: dict[str, Any]) -> tuple[str, str, list[str], list[str], list[str]]:
    title = article.get("title", "")
    snippet = article.get("snippet", "")
    content = article.get("content_text", "")

    base = content or snippet or title
    sentences = [s.strip() for s in base.replace("\n", " ").split(".") if s.strip()]
    lines = [f"{s}." for s in sentences[:3]] or ["요약할 본문이 부족합니다."]
    one_liner = lines[0]
    points = [f"핵심 {idx+1}: {line}" for idx, line in enumerate(lines[:3])]
    tags = article.get("tags", [])[:5] or [article.get("topic", "all")]
    return title, one_liner, lines, points, tags


def summarize_and_translate(article: dict[str, Any]) -> tuple[str, str, list[str], list[str], list[str]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _rule_based(article)

    client = OpenAI(api_key=api_key)
    prompt = f"""
아래 기사를 한국어로 자연스럽게 번역/요약해 주세요.
규칙:
- 과장 금지, 확인 불가 내용은 '불확실' 표시.
- 전문용어는 필요 시 한국어(원문) 병기.
- JSON만 출력: title_ko, one_liner, lines(3), points(3), tags(5)

제목: {article.get('title', '')}
본문: {article.get('content_text') or article.get('snippet', '')}
"""

    try:
        resp = client.responses.create(
            model=os.getenv("OPENAI_SUMMARY_MODEL", "gpt-4o-mini"),
            input=prompt,
            temperature=0.2,
        )
        text = resp.output_text
        import json

        payload = json.loads(text)
        return (
            payload.get("title_ko") or article.get("title", ""),
            payload.get("one_liner") or "",
            payload.get("lines") or [],
            payload.get("points") or [],
            payload.get("tags") or [],
        )
    except Exception:
        return _rule_based(article)
