"""API routes for the OSINT monitor."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session  # noqa: TC002

from backend.collectors import collect_rss
from backend.database.session import get_db

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
