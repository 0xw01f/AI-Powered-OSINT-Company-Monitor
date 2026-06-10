"""Monitoring service for watched companies and alerts."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from sqlalchemy import func

from backend.database.models import Article, Entity, MonitoredCompany

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


def search_articles_by_company(
    db: Session,
    name: str,
    limit: int = 20,
) -> list[Article]:
    """Return articles mentioning a specific company name (case-insensitive)."""
    return (
        db.query(Article)
        .join(Entity)
        .filter(func.lower(Entity.name) == func.lower(name))
        .order_by(Article.published_at.desc())
        .limit(limit)
        .all()
    )


def list_monitored_companies(db: Session) -> list[MonitoredCompany]:
    """Return all monitored companies ordered by name."""
    return db.query(MonitoredCompany).order_by(MonitoredCompany.name).all()


def add_monitored_company(db: Session, name: str) -> MonitoredCompany | None:
    """Add a company to the watchlist. Returns None if already exists."""
    existing = (
        db.query(MonitoredCompany)
        .filter(func.lower(MonitoredCompany.name) == func.lower(name))
        .first()
    )
    if existing is not None:
        return None
    company = MonitoredCompany(name=name)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def remove_monitored_company(db: Session, name: str) -> bool:
    """Remove a company from the watchlist. Returns True if removed."""
    company = (
        db.query(MonitoredCompany)
        .filter(func.lower(MonitoredCompany.name) == func.lower(name))
        .first()
    )
    if company is None:
        return False
    db.delete(company)
    db.commit()
    return True


def get_alerts(
    db: Session,
    hours: int = 24,
    limit: int = 50,
) -> list[Article]:
    """Return recent articles mentioning any monitored company."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    return (
        db.query(Article)
        .join(Entity)
        .join(MonitoredCompany, func.lower(Entity.name) == func.lower(MonitoredCompany.name))
        .filter(Article.created_at >= cutoff)
        .order_by(Article.created_at.desc())
        .limit(limit)
        .all()
    )
