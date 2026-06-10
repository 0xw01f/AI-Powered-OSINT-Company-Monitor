"""ORM models for the OSINT monitor database."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from backend.database.base import Base


class ArticleStatus(enum.StrEnum):
    """Processing status of an article."""

    PENDING = 'pending'
    SCRAPED = 'scraped'
    ANALYZED = 'analyzed'
    SUMMARIZED = 'summarized'
    ERROR = 'error'


class Article(Base):
    """News article scraped from public sources."""

    __tablename__ = 'articles'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    source: Mapped[str | None] = mapped_column(Text)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    content: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str | None] = mapped_column(String(32), index=True)
    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus),
        default=ArticleStatus.PENDING,
        nullable=False,
    )
    language: Mapped[str | None] = mapped_column(String(10))
    analysis: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    entities: Mapped[list[Entity]] = relationship(
        back_populates='article',
        cascade='all, delete-orphan',
    )


class Entity(Base):
    """Named entity extracted from an article."""

    __tablename__ = 'entities'

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(
        ForeignKey('articles.id'),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)

    article: Mapped[Article] = relationship(back_populates='entities')


class MonitoredCompany(Base):
    """Company explicitly watched by the user for alerts."""

    __tablename__ = 'monitored_companies'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
