"""Scraper service orchestrating article content extraction."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backend.database.models import Article, ArticleStatus
from backend.scrapers.article import scrape_article

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def scrape_pending_articles(db: Session, batch_size: int = 10) -> dict[str, int]:
    """Scrape content for PENDING articles and update their status."""
    pending = (
        db.query(Article)
        .filter_by(status=ArticleStatus.PENDING)
        .limit(batch_size)
        .all()
    )

    scraped_count = 0
    error_count = 0

    for article in pending:
        content = scrape_article(article.url)
        if content is not None:
            article.content = content
            article.status = ArticleStatus.SCRAPED
            scraped_count += 1
        else:
            article.status = ArticleStatus.ERROR
            error_count += 1

    db.commit()
    return {'scraped': scraped_count, 'errors': error_count}
