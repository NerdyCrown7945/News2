from __future__ import annotations

import json
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

import feedparser
import requests
from bs4 import BeautifulSoup

from .db import session_scope
from .llm import summarize_and_translate
from .models import Article
from .utils import canonicalize_url, is_article_like_url

SOURCES_PATH = Path(__file__).resolve().parents[1] / "sources.json"


def load_sources() -> list[dict[str, Any]]:
    return json.loads(SOURCES_PATH.read_text(encoding="utf-8"))


def extract_article_url(entry: Any) -> str:
    candidates: list[str] = []
    if getattr(entry, "link", None):
        candidates.append(entry.link)
    for link_obj in entry.get("links", []):
        if link_obj.get("rel") == "alternate" and link_obj.get("href"):
            candidates.append(link_obj["href"])
    for key in ("guid", "id"):
        value = entry.get(key)
        if isinstance(value, str) and value.startswith("http"):
            candidates.append(value)

    for raw in candidates:
        canon = canonicalize_url(raw)
        if is_article_like_url(canon):
            return canon
    return ""


def _html_to_text(url: str, fallback: str) -> str:
    if not url:
        return fallback
    try:
        response = requests.get(url, timeout=8, headers={"User-Agent": "news-digest-bot/1.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for bad in soup(["script", "style", "noscript"]):
            bad.extract()
        text = " ".join(soup.get_text(" ").split())
        return text[:6000] if text else fallback
    except Exception:
        return fallback


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def article_exists(url_canonical: str, title: str) -> bool:
    with session_scope() as session:
        if url_canonical:
            found = session.query(Article).filter(Article.url_canonical == url_canonical).first()
            if found:
                return True
        latest = (
            session.query(Article)
            .order_by(Article.id.desc())
            .limit(200)
            .all()
        )
        return any(_similar(item.title, title) > 0.92 for item in latest)


def ingest_from_sources(limit_per_source: int = 20) -> dict[str, int]:
    sources = [s for s in load_sources() if s.get("enabled", True)]
    inserted = 0
    failed = 0

    for source in sources:
        try:
            feed = feedparser.parse(source["feed_url"])
            for entry in feed.entries[:limit_per_source]:
                title = (entry.get("title") or "").strip()
                if not title:
                    continue
                article_url = extract_article_url(entry)
                snippet_html = entry.get("summary", "") or entry.get("description", "")
                snippet = BeautifulSoup(snippet_html, "html.parser").get_text(" ", strip=True)[:1000]
                content_text = _html_to_text(article_url, snippet)
                if article_exists(article_url, title):
                    continue

                article_dict = {
                    "title": title,
                    "snippet": snippet,
                    "content_text": content_text,
                    "tags": source.get("tags", []),
                    "topic": source.get("topic", "all"),
                }
                title_ko, one_liner, lines, points, tags = summarize_and_translate(article_dict)
                published_parsed = entry.get("published_parsed") or entry.get("updated_parsed")
                published_at = (
                    datetime(*published_parsed[:6], tzinfo=timezone.utc).isoformat()
                    if published_parsed
                    else ""
                )

                with session_scope() as session:
                    session.add(
                        Article(
                            title=title,
                            title_ko=title_ko,
                            url=article_url,
                            url_canonical=article_url,
                            source=source["name"],
                            topic=source.get("topic", "all"),
                            published_at=published_at,
                            fetched_at=datetime.now(timezone.utc).isoformat(),
                            snippet=snippet,
                            content_text=content_text,
                            summary_one_liner_ko=one_liner,
                            summary_lines_ko=lines,
                            key_points_ko=points,
                            tags=tags,
                            lang=source.get("language_hint", "en"),
                            cluster_id="",
                        )
                    )
                inserted += 1
        except Exception:
            failed += 1
            continue

    return {"inserted": inserted, "failed_sources": failed, "source_count": len(sources)}
