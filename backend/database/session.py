"""Database engine and session management."""

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database.base import Base

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://osint:osint@localhost:5432/osint_monitor',
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Create all tables defined in the metadata."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Iterator[Session]:
    """Yield a database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
