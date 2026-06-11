"""RSS collector using feedparser."""

from __future__ import annotations

import calendar
import hashlib
import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import feedparser

from backend.database.models import Article, ArticleStatus, Source

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


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


def fetch_rss_feed(url: str, timeout: int = 15) -> list[dict[str, Any]]:
    """Fetch and parse an RSS feed safely, returning structured entries."""
    try:
        with urlopen(url, timeout=timeout) as response:  # noqa: S310
            content = response.read()
        parsed = feedparser.parse(content)
        if hasattr(parsed, 'bozo') and parsed.bozo:
            logger.warning('Feed %s has errors: %s', url, parsed.bozo_exception)
        return [_parse_entry(entry) for entry in parsed.entries]
    except (URLError, HTTPError, TimeoutError, OSError) as exc:
        logger.error('Failed to fetch RSS %s: %s', url, exc)
        return []
    except Exception as exc:  # noqa: BLE001
        logger.error('Unexpected error fetching RSS %s: %s', url, exc)
        return []


def collect_rss(
    db: Session,
    limit_per_source: int = 20,
    max_sources: int = 20,
    min_priority: int | None = None,
) -> dict[str, int]:
    """Collect articles from active RSS sources in the database."""
    query = db.query(Source).filter_by(active=True).filter(Source.rss_available.is_(True))
    if min_priority is not None:
        query = query.filter(Source.priority >= min_priority)
    # Sort by priority descending so most important sources are processed first
    query = query.order_by(Source.priority.desc().nullslast())
    sources = query.limit(max_sources).all()

    total_inserted = 0
    total_skipped = 0
    seen_urls: set[str] = set()

    for source in sources:
        entries = fetch_rss_feed(source.url)
        for entry in entries[:limit_per_source]:
            url = entry.get('url')
            title = entry.get('title')
            if not url or not title:
                continue

            normalized_url = url.strip()
            if normalized_url in seen_urls:
                total_skipped += 1
                continue

            existing = db.query(Article).filter_by(url=normalized_url).first()
            if existing:
                total_skipped += 1
                seen_urls.add(normalized_url)
                continue

            content_hash = hashlib.sha256(normalized_url.encode()).hexdigest()[:32]
            article = Article(
                title=title,
                url=normalized_url,
                source=source.name,
                summary=entry.get('summary'),
                published_at=entry.get('published_at'),
                content_hash=content_hash,
                status=ArticleStatus.PENDING,
                language=source.language,
            )
            db.add(article)
            seen_urls.add(normalized_url)
            total_inserted += 1

    db.commit()
    return {'inserted': total_inserted, 'skipped': total_skipped}
