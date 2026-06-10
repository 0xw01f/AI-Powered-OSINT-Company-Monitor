"""Source management: CSV import and CRUD operations."""

from __future__ import annotations

import csv
import logging
import pathlib
from typing import TYPE_CHECKING, Any

from sqlalchemy import func

from backend.database.models import Source

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def _parse_bool(value: str) -> bool:
    """Parse a CSV boolean string."""
    return value.strip().lower() in ('true', 'yes', '1')


def import_sources_from_csv(db: Session, csv_path: pathlib.Path | None = None) -> int:
    """Seed the database from CSV if the sources table is empty.

    Returns the number of sources imported.
    """
    existing = db.query(Source).first()
    if existing is not None:
        return 0

    if csv_path is None:
        csv_path = pathlib.Path(__file__).parents[1] / 'config' / 'sources.csv'

    imported = 0
    with open(csv_path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.add(
                Source(
                    id=int(row['id']),
                    name=row['name'],
                    url=row['url'],
                    category=row.get('category') or None,
                    language=row.get('language') or None,
                    domain=row.get('domain') or None,
                    subdomain=row.get('subdomain') or None,
                    source_type=row.get('source_type') or None,
                    country=row.get('country') or None,
                    geographic_scope=row.get('geographic_scope') or None,
                    reliability=_parse_int(row.get('reliability')),
                    priority=_parse_int(row.get('priority')),
                    update_frequency=row.get('update_frequency') or None,
                    entity_focus=row.get('entity_focus') or None,
                    rss_available=_parse_bool(row.get('rss_available', 'true')),
                    active=_parse_bool(row.get('active', 'true')),
                    tags=row.get('tags') or None,
                ),
            )
            imported += 1

    db.commit()
    logger.info('Imported %d sources from %s', imported, csv_path)
    return imported


def _parse_int(value: str | None) -> int | None:
    """Parse an integer string, returning None on empty input."""
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def list_sources(  # noqa: PLR0913
    db: Session,
    active_only: bool = False,
    category: str | None = None,
    country: str | None = None,
    min_reliability: int | None = None,
    min_priority: int | None = None,
) -> list[Source]:
    """List sources with optional filters."""
    query = db.query(Source)
    if active_only:
        query = query.filter_by(active=True)
    if category:
        query = query.filter(func.lower(Source.category) == func.lower(category))
    if country:
        query = query.filter(func.lower(Source.country) == func.lower(country))
    if min_reliability is not None:
        query = query.filter(Source.reliability >= min_reliability)
    if min_priority is not None:
        query = query.filter(Source.priority >= min_priority)
    return query.order_by(Source.priority.desc()).all()


def get_source(db: Session, source_id: int) -> Source | None:
    """Get a single source by ID."""
    return db.query(Source).filter_by(id=source_id).first()


def create_source(db: Session, data: dict[str, Any]) -> Source:
    """Create a new source."""
    source = Source(**data)
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def update_source(db: Session, source_id: int, data: dict[str, Any]) -> Source | None:
    """Update an existing source."""
    source = get_source(db, source_id)
    if source is None:
        return None
    for key, value in data.items():
        if hasattr(source, key):
            setattr(source, key, value)
    db.commit()
    db.refresh(source)
    return source


def delete_source(db: Session, source_id: int) -> bool:
    """Delete a source. Returns True if deleted."""
    source = get_source(db, source_id)
    if source is None:
        return False
    db.delete(source)
    db.commit()
    return True


def toggle_source(db: Session, source_id: int) -> Source | None:
    """Toggle the active status of a source."""
    source = get_source(db, source_id)
    if source is None:
        return None
    source.active = not source.active
    db.commit()
    db.refresh(source)
    return source
