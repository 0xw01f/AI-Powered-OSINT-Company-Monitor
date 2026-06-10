"""FastAPI entry point for the OSINT monitor backend."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.database import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Initialize database tables on application startup."""
    init_db()
    yield


app = FastAPI(
    title='AI-Powered OSINT Company Monitor',
    lifespan=lifespan,
)


@app.get('/')
def read_root() -> dict[str, str]:
    """Health check endpoint."""
    return {'message': 'OSINT Monitor API is running'}
