"""Unit tests for source management service."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database.base import Base
from backend.services.sources import (
    create_source,
    delete_source,
    get_source,
    list_sources,
    toggle_source,
    update_source,
)


@pytest.fixture
def db_session() -> Iterator[Session]:
    """Create an in-memory SQLite session for testing."""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    yield session
    session.close()
    engine.dispose()


class TestSourceCrud:
    """Test suite for source CRUD operations."""

    def test_create_source(self, db_session: Session) -> None:
        """Should create a new source."""
        source = create_source(db_session, {'name': 'Test', 'url': 'http://test.com'})
        assert source.name == 'Test'
        assert source.url == 'http://test.com'

    def test_get_source(self, db_session: Session) -> None:
        """Should retrieve a source by ID."""
        created = create_source(db_session, {'name': 'Test', 'url': 'http://test.com'})
        fetched = get_source(db_session, created.id)
        assert fetched is not None
        assert fetched.name == 'Test'

    def test_get_nonexistent_returns_none(self, db_session: Session) -> None:
        """Should return None for missing source."""
        assert get_source(db_session, 999) is None

    def test_list_sources(self, db_session: Session) -> None:
        """Should list all sources ordered by priority."""
        create_source(db_session, {'name': 'Low', 'url': 'http://low.com', 'priority': 10})
        create_source(db_session, {'name': 'High', 'url': 'http://high.com', 'priority': 90})
        results = list_sources(db_session)
        assert len(results) == 2
        assert results[0].name == 'High'

    def test_list_sources_active_only(self, db_session: Session) -> None:
        """Should filter by active status."""
        create_source(db_session, {'name': 'Active', 'url': 'http://a.com', 'active': True})
        create_source(db_session, {'name': 'Inactive', 'url': 'http://i.com', 'active': False})
        results = list_sources(db_session, active_only=True)
        assert len(results) == 1
        assert results[0].name == 'Active'

    def test_list_sources_by_category(self, db_session: Session) -> None:
        """Should filter by category."""
        create_source(db_session, {'name': 'Sec', 'url': 'http://s.com', 'category': 'security'})
        create_source(db_session, {'name': 'Tech', 'url': 'http://t.com', 'category': 'tech'})
        results = list_sources(db_session, category='security')
        assert len(results) == 1
        assert results[0].name == 'Sec'

    def test_update_source(self, db_session: Session) -> None:
        """Should update source fields."""
        created = create_source(db_session, {'name': 'Old', 'url': 'http://old.com'})
        updated = update_source(db_session, created.id, {'name': 'New'})
        assert updated is not None
        assert updated.name == 'New'

    def test_update_nonexistent_returns_none(self, db_session: Session) -> None:
        """Should return None when updating missing source."""
        assert update_source(db_session, 999, {'name': 'X'}) is None

    def test_delete_source(self, db_session: Session) -> None:
        """Should delete an existing source."""
        created = create_source(db_session, {'name': 'Del', 'url': 'http://del.com'})
        assert delete_source(db_session, created.id) is True
        assert get_source(db_session, created.id) is None

    def test_delete_nonexistent_returns_false(self, db_session: Session) -> None:
        """Should return False when deleting missing source."""
        assert delete_source(db_session, 999) is False

    def test_toggle_source(self, db_session: Session) -> None:
        """Should flip active status."""
        created = create_source(db_session, {'name': 'Tog', 'url': 'http://tog.com', 'active': True})
        toggled = toggle_source(db_session, created.id)
        assert toggled is not None
        assert toggled.active is False
        toggled_again = toggle_source(db_session, created.id)
        assert toggled_again is not None
        assert toggled_again.active is True

    def test_toggle_nonexistent_returns_none(self, db_session: Session) -> None:
        """Should return None when toggling missing source."""
        assert toggle_source(db_session, 999) is None
