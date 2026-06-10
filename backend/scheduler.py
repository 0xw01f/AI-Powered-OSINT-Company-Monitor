"""Background scheduler for automated OSINT collection.

NOTE: APScheduler is used for MVP simplicity. For production,
this should be replaced by a distributed task queue such as
Celery + Redis for better reliability and scalability.
"""

from __future__ import annotations

import logging
from typing import Any

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.collectors.rss import collect_rss
from backend.database.session import SessionLocal
from backend.services.ner import analyze_articles
from backend.services.scraper import scrape_pending_articles

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _run_rss_collection() -> None:
    """Collect RSS feeds."""
    db = SessionLocal()
    try:
        result = collect_rss(db, limit_per_source=20)
        logger.info('Scheduled RSS collection: %s', result)
    except Exception:
        logger.exception('RSS collection failed')
    finally:
        db.close()


def _run_scraping() -> None:
    """Scrape pending articles."""
    db = SessionLocal()
    try:
        result = scrape_pending_articles(db, batch_size=10)
        logger.info('Scheduled scraping: %s', result)
    except Exception:
        logger.exception('Scraping failed')
    finally:
        db.close()


def _run_ner() -> None:
    """Analyze scraped articles."""
    db = SessionLocal()
    try:
        result = analyze_articles(db, method='hybrid', batch_size=10)
        logger.info('Scheduled NER analysis: %s', result)
    except Exception:
        logger.exception('NER analysis failed')
    finally:
        db.close()


def start_scheduler() -> None:
    """Start the background scheduler."""
    global _scheduler  # noqa: PLW0603
    if _scheduler is not None:
        return
    _scheduler = BackgroundScheduler()
    _scheduler.add_job(
        _run_rss_collection,
        IntervalTrigger(minutes=30),
        id='rss',
        replace_existing=True,
    )
    _scheduler.add_job(
        _run_scraping,
        IntervalTrigger(minutes=15),
        id='scrape',
        replace_existing=True,
    )
    _scheduler.add_job(
        _run_ner,
        IntervalTrigger(minutes=15),
        id='ner',
        replace_existing=True,
    )
    _scheduler.start()
    logger.info('Background scheduler started')


def stop_scheduler() -> None:
    """Stop the background scheduler."""
    global _scheduler  # noqa: PLW0603
    if _scheduler is not None:
        _scheduler.shutdown()
        _scheduler = None
        logger.info('Background scheduler stopped')


def get_scheduler_status() -> dict[str, Any]:
    """Return current scheduler status and job list."""
    if _scheduler is None:
        return {'running': False, 'jobs': []}
    jobs = [
        {
            'id': job.id,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
        }
        for job in _scheduler.get_jobs()
    ]
    return {'running': _scheduler.running, 'jobs': jobs}
