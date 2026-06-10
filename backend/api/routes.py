"""API routes for the OSINT monitor."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session  # noqa: TC002

from backend.collectors import collect_rss
from backend.database.session import get_db
from backend.nlp.benchmark import benchmark_text
from backend.scheduler import get_scheduler_status
from backend.services.monitor import (
    add_monitored_company,
    get_alerts,
    list_monitored_companies,
    remove_monitored_company,
    search_articles_by_company,
)
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


@router.get('/monitor/search')
def monitor_search(
    db: Annotated[Session, Depends(get_db)],
    name: str,
    limit: int = 20,
) -> list[dict[str, str | int | None]]:
    """Search articles mentioning a specific company."""
    articles = search_articles_by_company(db, name=name, limit=limit)
    return [
        {
            'id': article.id,
            'title': article.title,
            'url': article.url,
            'source': article.source,
            'published_at': article.published_at.isoformat() if article.published_at else None,
        }
        for article in articles
    ]


@router.post('/monitor/watch')
def monitor_watch(
    db: Annotated[Session, Depends(get_db)],
    name: str,
) -> dict[str, str]:
    """Add a company to the watchlist."""
    result = add_monitored_company(db, name=name)
    if result is None:
        return {'status': 'already_exists', 'name': name}
    return {'status': 'added', 'name': result.name}


@router.delete('/monitor/watch')
def monitor_unwatch(
    db: Annotated[Session, Depends(get_db)],
    name: str,
) -> dict[str, str]:
    """Remove a company from the watchlist."""
    removed = remove_monitored_company(db, name=name)
    if not removed:
        return {'status': 'not_found', 'name': name}
    return {'status': 'removed', 'name': name}


@router.get('/monitor/watched')
def monitor_watched(
    db: Annotated[Session, Depends(get_db)],
) -> list[dict[str, str]]:
    """List all monitored companies."""
    companies = list_monitored_companies(db)
    return [{'name': c.name} for c in companies]


@router.get('/monitor/alerts')
def monitor_alerts(
    db: Annotated[Session, Depends(get_db)],
    hours: int = 24,
    limit: int = 50,
) -> list[dict[str, str | int | None]]:
    """Get recent articles mentioning watched companies."""
    articles = get_alerts(db, hours=hours, limit=limit)
    return [
        {
            'id': article.id,
            'title': article.title,
            'url': article.url,
            'source': article.source,
            'published_at': article.published_at.isoformat() if article.published_at else None,
        }
        for article in articles
    ]


@router.get('/scheduler/status')
def scheduler_status() -> dict[str, Any]:
    """Return background scheduler status."""
    return get_scheduler_status()
