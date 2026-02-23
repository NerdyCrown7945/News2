from __future__ import annotations

from sqlalchemy import DateTime, Integer, String, Text, JSON, Index
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(600), default="")
    title_ko: Mapped[str] = mapped_column(String(600), default="")
    url: Mapped[str] = mapped_column(String(1000), default="")
    url_canonical: Mapped[str] = mapped_column(String(1000), index=True, default="")
    source: Mapped[str] = mapped_column(String(200), index=True, default="")
    topic: Mapped[str] = mapped_column(String(50), index=True, default="all")
    published_at: Mapped[str] = mapped_column(String(40), index=True, default="")
    fetched_at: Mapped[str] = mapped_column(String(40), index=True, default="")
    snippet: Mapped[str] = mapped_column(Text, default="")
    content_text: Mapped[str] = mapped_column(Text, default="")
    summary_one_liner_ko: Mapped[str] = mapped_column(Text, default="")
    summary_lines_ko: Mapped[list] = mapped_column(JSON, default=list)
    key_points_ko: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    lang: Mapped[str] = mapped_column(String(30), default="en")
    cluster_id: Mapped[str] = mapped_column(String(120), default="")


Index("idx_articles_topic_published", Article.topic, Article.published_at)
