"""FastAPI entry point for the OSINT monitor backend."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.api import router
from backend.database import get_db, init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Initialize database tables on application startup."""
    init_db()
    yield


app = FastAPI(
    title='AI-Powered OSINT Company Monitor',
    lifespan=lifespan,
)
app.include_router(router)


@app.get('/')
def read_root() -> dict[str, str]:
    """Health check endpoint."""
    return {'message': 'OSINT Monitor API is running'}


@app.get('/health')
def health_check(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    """Verify database connectivity."""
    try:
        db.execute(text('SELECT 1'))
    except Exception:
        return {'status': 'error', 'database': 'disconnected'}
    return {'status': 'ok', 'database': 'connected'}
