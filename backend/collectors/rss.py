"""RSS collector using feedparser."""

from __future__ import annotations

import calendar
import hashlib
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import feedparser

from backend.config import load_sources
from backend.database.models import Article, ArticleStatus

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def _parse_entry(entry: Any) -> dict[str, Any]:
    """Extract structured data from a feedparser entry."""
    published: datetime | None = None
    published_parsed = entry.get('published_parsed')
    if published_parsed is not None:
        published = datetime.fromtimestamp(
            calendar.timegm(published_parsed),
            tz=timezone.utc,
        )
    return {
        'title': entry.get('title'),
        'url': entry.get('link'),
        'summary': entry.get('summary'),
        'published_at': published,
    }


def fetch_rss_feed(url: str) -> list[dict[str, Any]]:
    """Fetch and parse an RSS feed, returning structured entries."""
    parsed = feedparser.parse(url)
    return [_parse_entry(entry) for entry in parsed.entries]


def collect_rss(db: Session, limit_per_source: int = 20) -> dict[str, int]:
    """Collect articles from all configured RSS sources."""
    sources = load_sources()
    total_inserted = 0
    total_skipped = 0

    for source in sources:
        entries = fetch_rss_feed(source.url)
        for entry in entries[:limit_per_source]:
            url = entry.get('url')
            title = entry.get('title')
            if not url or not title:
                continue

            existing = db.query(Article).filter_by(url=url).first()
            if existing:
                total_skipped += 1
                continue

            content_hash = hashlib.sha256(url.encode()).hexdigest()[:32]
            article = Article(
                title=title,
                url=url,
                source=source.name,
                summary=entry.get('summary'),
                published_at=entry.get('published_at'),
                content_hash=content_hash,
                status=ArticleStatus.PENDING,
                language=source.language,
            )
            db.add(article)
            total_inserted += 1

    db.commit()
    return {'inserted': total_inserted, 'skipped': total_skipped}
