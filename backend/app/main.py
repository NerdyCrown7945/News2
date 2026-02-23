from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine, session_scope
from .ingest import ingest_from_sources
from .models import Article

app = FastAPI(title="AI SciTech News Digest API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ingest/run")
def run_ingest() -> dict:
    return ingest_from_sources()


def _range_start(range_value: str) -> Optional[datetime]:
    now = datetime.now(timezone.utc)
    mapping = {
        "24h": now - timedelta(hours=24),
        "7d": now - timedelta(days=7),
        "30d": now - timedelta(days=30),
    }
    return mapping.get(range_value)


@app.get("/feed")
def feed(
    topic: str = "all",
    range: str = Query("7d", alias="range"),
    query: str = "",
    sort: str = "new",
):
    start = _range_start(range)
    with session_scope() as session:
        q = session.query(Article)
        if topic != "all":
            q = q.filter(Article.topic == topic)
        if query:
            like = f"%{query}%"
            q = q.filter((Article.title.ilike(like)) | (Article.summary_one_liner_ko.ilike(like)))
        if start:
            q = q.filter(Article.published_at >= start.isoformat())
        if sort == "new":
            q = q.order_by(Article.published_at.desc(), Article.id.desc())
        articles = q.limit(300).all()

    return {
        "items": [
            {
                "id": a.id,
                "title": a.title,
                "title_ko": a.title_ko,
                "url": a.url,
                "source": a.source,
                "topic": a.topic,
                "published_at": a.published_at,
                "summary_one_liner_ko": a.summary_one_liner_ko,
                "tags": a.tags,
            }
            for a in articles
        ]
    }


@app.get("/article/{article_id}")
def article_detail(article_id: int):
    with session_scope() as session:
        article = session.query(Article).filter(Article.id == article_id).first()
    if not article:
        return {"error": "not_found"}
    return {
        "id": article.id,
        "title": article.title,
        "title_ko": article.title_ko,
        "url": article.url,
        "source": article.source,
        "topic": article.topic,
        "published_at": article.published_at,
        "snippet": article.snippet,
        "summary_one_liner_ko": article.summary_one_liner_ko,
        "summary_lines_ko": article.summary_lines_ko,
        "key_points_ko": article.key_points_ko,
        "tags": article.tags,
    }


@app.get("/search")
def search(
    query: str,
    from_date: str = Query("", alias="from"),
    to_date: str = Query("", alias="to"),
    topic: str = "all",
    tag: str = "",
):
    with session_scope() as session:
        q = session.query(Article)
        if query:
            like = f"%{query}%"
            q = q.filter(
                (Article.title.ilike(like))
                | (Article.title_ko.ilike(like))
                | (Article.summary_one_liner_ko.ilike(like))
            )
        if topic != "all":
            q = q.filter(Article.topic == topic)
        if from_date:
            q = q.filter(Article.published_at >= f"{from_date}T00:00:00+00:00")
        if to_date:
            q = q.filter(Article.published_at <= f"{to_date}T23:59:59+00:00")
        articles = q.order_by(Article.published_at.desc()).limit(500).all()

    items = []
    for a in articles:
        if tag and tag not in (a.tags or []):
            continue
        items.append(
            {
                "id": a.id,
                "title": a.title,
                "title_ko": a.title_ko,
                "published_at": a.published_at,
                "source": a.source,
                "topic": a.topic,
                "tags": a.tags,
            }
        )
    return {"items": items}
