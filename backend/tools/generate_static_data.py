from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.db import Base, engine, session_scope
from app.ingest import ingest_from_sources
from app.models import Article
from app.utils import is_article_like_url

BASE_DIR = Path(__file__).resolve().parents[2]
PUBLIC_DATA_DIR = BASE_DIR / "frontend" / "public" / "data"
ARTICLES_DIR = PUBLIC_DATA_DIR / "articles"


def generate(max_articles: int = 150):
    Base.metadata.create_all(bind=engine)
    ingest_from_sources(limit_per_source=8)

    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)
    with session_scope() as session:
        items = session.query(Article).order_by(Article.published_at.desc(), Article.id.desc()).limit(max_articles).all()

    feed = []
    for a in items:
        safe_url = a.url if is_article_like_url(a.url) else ""
        feed.append(
            {
                "id": a.id,
                "title": a.title,
                "title_ko": a.title_ko,
                "url": safe_url,
                "source": a.source,
                "topic": a.topic,
                "published_at": a.published_at,
                "summary_one_liner_ko": a.summary_one_liner_ko,
                "tags": a.tags,
            }
        )
        (ARTICLES_DIR / f"{a.id}.json").write_text(
            json.dumps(
                {
                    "id": a.id,
                    "title": a.title,
                    "title_ko": a.title_ko,
                    "url": safe_url,
                    "source": a.source,
                    "topic": a.topic,
                    "published_at": a.published_at,
                    "snippet": a.snippet,
                    "summary_one_liner_ko": a.summary_one_liner_ko,
                    "summary_lines_ko": a.summary_lines_ko,
                    "key_points_ko": a.key_points_ko,
                    "tags": a.tags,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    PUBLIC_DATA_DIR.mkdir(parents=True, exist_ok=True)
    (PUBLIC_DATA_DIR / "feed.json").write_text(
        json.dumps({"items": feed}, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-articles", type=int, default=150)
    args = parser.parse_args()
    generate(max_articles=args.max_articles)
