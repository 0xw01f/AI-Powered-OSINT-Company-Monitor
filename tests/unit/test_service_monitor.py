"""Unit tests for the monitoring service."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database.base import Base
from backend.database.models import Article, ArticleStatus, Entity
from backend.services.monitor import (
    add_monitored_company,
    get_alerts,
    list_monitored_companies,
    remove_monitored_company,
    search_articles_by_company,
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


class TestSearchArticlesByCompany:
    """Test suite for search_articles_by_company."""

    def test_finds_articles_by_entity_name(self, db_session: Session) -> None:
        """Should return articles linked to a specific entity."""
        article = Article(
            title='Tesla News',
            url='http://example.com/tesla',
            status=ArticleStatus.ANALYZED,
        )
        db_session.add(article)
        db_session.commit()
        db_session.add(Entity(article_id=article.id, name='Tesla', type='Company'))
        db_session.commit()

        results = search_articles_by_company(db_session, name='Tesla')

        assert len(results) == 1
        assert results[0].title == 'Tesla News'

    def test_case_insensitive_search(self, db_session: Session) -> None:
        """Search should be case-insensitive."""
        article = Article(
            title='Apple News',
            url='http://example.com/apple',
            status=ArticleStatus.ANALYZED,
        )
        db_session.add(article)
        db_session.commit()
        db_session.add(Entity(article_id=article.id, name='Apple', type='Company'))
        db_session.commit()

        results = search_articles_by_company(db_session, name='apple')

        assert len(results) == 1

    def test_empty_when_no_match(self, db_session: Session) -> None:
        """Should return empty list when no entity matches."""
        results = search_articles_by_company(db_session, name='NonExistent')
        assert results == []


class TestMonitoredCompanies:
    """Test suite for watchlist CRUD."""

    def test_add_monitored_company(self, db_session: Session) -> None:
        """Should add a new company to the watchlist."""
        result = add_monitored_company(db_session, 'Tesla')

        assert result is not None
        assert result.name == 'Tesla'

    def test_add_duplicate_returns_none(self, db_session: Session) -> None:
        """Adding a duplicate should return None."""
        add_monitored_company(db_session, 'Tesla')
        result = add_monitored_company(db_session, 'tesla')

        assert result is None

    def test_list_monitored_companies(self, db_session: Session) -> None:
        """Should return all monitored companies ordered by name."""
        add_monitored_company(db_session, 'Apple')
        add_monitored_company(db_session, 'Tesla')

        results = list_monitored_companies(db_session)

        assert len(results) == 2
        assert results[0].name == 'Apple'
        assert results[1].name == 'Tesla'

    def test_remove_monitored_company(self, db_session: Session) -> None:
        """Should remove an existing company."""
        add_monitored_company(db_session, 'Tesla')
        removed = remove_monitored_company(db_session, 'tesla')

        assert removed is True
        assert list_monitored_companies(db_session) == []

    def test_remove_nonexistent_returns_false(self, db_session: Session) -> None:
        """Removing a non-existent company should return False."""
        removed = remove_monitored_company(db_session, 'Tesla')
        assert removed is False


class TestGetAlerts:
    """Test suite for get_alerts."""

    def test_returns_recent_articles_for_watched_companies(self, db_session: Session) -> None:
        """Should return articles mentioning watched companies."""
        add_monitored_company(db_session, 'Tesla')

        article = Article(
            title='Tesla Alert',
            url='http://example.com/alert',
            status=ArticleStatus.ANALYZED,
        )
        db_session.add(article)
        db_session.commit()
        db_session.add(Entity(article_id=article.id, name='Tesla', type='Company'))
        db_session.commit()

        results = get_alerts(db_session, hours=24)

        assert len(results) == 1
        assert results[0].title == 'Tesla Alert'

    def test_ignores_old_articles(self, db_session: Session) -> None:
        """Should not return articles older than the cutoff."""
        add_monitored_company(db_session, 'Tesla')

        article = Article(
            title='Old News',
            url='http://example.com/old',
            status=ArticleStatus.ANALYZED,
        )
        db_session.add(article)
        db_session.commit()
        db_session.add(Entity(article_id=article.id, name='Tesla', type='Company'))
        db_session.commit()

        results = get_alerts(db_session, hours=0)

        assert results == []
