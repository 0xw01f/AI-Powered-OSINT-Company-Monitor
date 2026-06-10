"""API routes for source management."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session  # noqa: TC002

from backend.database.session import get_db
from backend.services.sources import (
    create_source,
    delete_source,
    get_source,
    list_sources,
    toggle_source,
    update_source,
)

router = APIRouter(prefix='/sources', tags=['sources'])


@router.get('/')
def sources_list(  # noqa: PLR0913
    db: Annotated[Session, Depends(get_db)],
    active_only: bool = False,
    category: str | None = None,
    country: str | None = None,
    min_reliability: int | None = None,
    min_priority: int | None = None,
) -> list[dict[str, Any]]:
    """List all sources with optional filters."""
    items = list_sources(
        db,
        active_only=active_only,
        category=category,
        country=country,
        min_reliability=min_reliability,
        min_priority=min_priority,
    )
    return [
        {
            'id': s.id,
            'name': s.name,
            'url': s.url,
            'category': s.category,
            'language': s.language,
            'country': s.country,
            'reliability': s.reliability,
            'priority': s.priority,
            'active': s.active,
            'tags': s.tags,
        }
        for s in items
    ]


@router.post('/')
def sources_create(
    db: Annotated[Session, Depends(get_db)],
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Create a new source."""
    source = create_source(db, payload)
    return {
        'status': 'created',
        'id': source.id,
        'name': source.name,
    }


@router.get('/{source_id}')
def sources_get(
    db: Annotated[Session, Depends(get_db)],
    source_id: int,
) -> dict[str, Any]:
    """Get a single source by ID."""
    source = get_source(db, source_id)
    if source is None:
        return {'status': 'not_found'}
    return {
        'id': source.id,
        'name': source.name,
        'url': source.url,
        'category': source.category,
        'language': source.language,
        'domain': source.domain,
        'subdomain': source.subdomain,
        'source_type': source.source_type,
        'country': source.country,
        'geographic_scope': source.geographic_scope,
        'reliability': source.reliability,
        'priority': source.priority,
        'update_frequency': source.update_frequency,
        'entity_focus': source.entity_focus,
        'rss_available': source.rss_available,
        'active': source.active,
        'tags': source.tags,
    }


@router.put('/{source_id}')
def sources_update(
    db: Annotated[Session, Depends(get_db)],
    source_id: int,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Update an existing source."""
    source = update_source(db, source_id, payload)
    if source is None:
        return {'status': 'not_found'}
    return {'status': 'updated', 'id': source.id}


@router.delete('/{source_id}')
def sources_delete(
    db: Annotated[Session, Depends(get_db)],
    source_id: int,
) -> dict[str, str]:
    """Delete a source."""
    deleted = delete_source(db, source_id)
    if not deleted:
        return {'status': 'not_found'}
    return {'status': 'deleted'}


@router.post('/{source_id}/toggle')
def sources_toggle(
    db: Annotated[Session, Depends(get_db)],
    source_id: int,
) -> dict[str, Any]:
    """Toggle the active status of a source."""
    source = toggle_source(db, source_id)
    if source is None:
        return {'status': 'not_found'}
    return {'status': 'toggled', 'id': source.id, 'active': source.active}
