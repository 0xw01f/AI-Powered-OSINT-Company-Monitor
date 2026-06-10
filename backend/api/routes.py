"""API routes for the OSINT monitor."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session  # noqa: TC002

from backend.collectors import collect_rss
from backend.database.session import get_db
from backend.services.scraper import scrape_pending_articles

router = APIRouter(prefix='/collect', tags=['collect'])


@router.post('/rss')
def collect_rss_endpoint(
    db: Annotated[Session, Depends(get_db)],
    limit_per_source: int = 20,
) -> dict[str, str | int]:
    """Trigger RSS collection from all configured sources."""
    result = collect_rss(db, limit_per_source=limit_per_source)
    return {
        'status': 'success',
        'inserted': result['inserted'],
        'skipped': result['skipped'],
    }


@router.post('/scrape')
def scrape_endpoint(
    db: Annotated[Session, Depends(get_db)],
    batch_size: int = 10,
) -> dict[str, str | int]:
    """Trigger scraping for pending articles."""
    result = scrape_pending_articles(db, batch_size=batch_size)
    return {
        'status': 'success',
        'scraped': result['scraped'],
        'errors': result['errors'],
    }
