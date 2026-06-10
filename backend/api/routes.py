"""API routes for the OSINT monitor."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session  # noqa: TC002

from backend.collectors import collect_rss
from backend.database.session import get_db
from backend.nlp.benchmark import benchmark_text
from backend.services.ner import analyze_articles
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


@router.post('/analyze')
def analyze_endpoint(
    db: Annotated[Session, Depends(get_db)],
    method: str = 'hybrid',
    batch_size: int = 10,
) -> dict[str, str | int | float]:
    """Trigger entity extraction on scraped articles."""
    result = analyze_articles(db, method=method, batch_size=batch_size)
    return {
        'status': 'success',
        'analyzed': result['analyzed'],
        'entities_found': result['entities_found'],
        'duration_ms': result['duration_ms'],
    }


@router.post('/benchmark')
def benchmark_endpoint(text: str, language: str = 'en') -> dict[str, Any]:
    """Benchmark NER methods on provided text."""
    return benchmark_text(text, language=language)
