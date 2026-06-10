"""Unit tests for the scraper service."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database.base import Base
from backend.database.models import Article, ArticleStatus
from backend.services.scraper import scrape_pending_articles


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


class TestScrapePendingArticles:
    """Test suite for scrape_pending_articles."""

    def test_scrapes_pending_and_updates_status(self, db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
        """Successful scraping should update content and status to SCRAPED."""
        def mock_scrape(url: str) -> str:
            return f'Content for {url}'

        monkeypatch.setattr('backend.services.scraper.scrape_article', mock_scrape)

        article = Article(
            title='Test Article',
            url='http://example.com/article',
            status=ArticleStatus.PENDING,
        )
        db_session.add(article)
        db_session.commit()

        result = scrape_pending_articles(db_session)

        assert result['scraped'] == 1
        assert result['errors'] == 0
        assert article.content == 'Content for http://example.com/article'
        assert article.status == ArticleStatus.SCRAPED

    def test_sets_error_on_failure(self, db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
        """Failed scraping should set status to ERROR."""
        def mock_scrape(url: str) -> None:
            return None

        monkeypatch.setattr('backend.services.scraper.scrape_article', mock_scrape)

        article = Article(
            title='Fail Article',
            url='http://example.com/fail',
            status=ArticleStatus.PENDING,
        )
        db_session.add(article)
        db_session.commit()

        result = scrape_pending_articles(db_session)

        assert result['scraped'] == 0
        assert result['errors'] == 1
        assert article.content is None
        assert article.status == ArticleStatus.ERROR

    def test_respects_batch_size(self, db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
        """Only process up to batch_size articles."""
        def mock_scrape(url: str) -> str:
            return 'content'

        monkeypatch.setattr('backend.services.scraper.scrape_article', mock_scrape)

        for i in range(5):
            db_session.add(Article(
                title=f'Article {i}',
                url=f'http://example.com/{i}',
                status=ArticleStatus.PENDING,
            ))
        db_session.commit()

        result = scrape_pending_articles(db_session, batch_size=2)

        assert result['scraped'] == 2
        assert result['errors'] == 0

    def test_ignores_non_pending(self, db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
        """Articles with status other than PENDING should not be processed."""
        def mock_scrape(url: str) -> str:
            return 'content'

        monkeypatch.setattr('backend.services.scraper.scrape_article', mock_scrape)

        db_session.add(Article(
            title='Already Scraped',
            url='http://example.com/scraped',
            status=ArticleStatus.SCRAPED,
        ))
        db_session.commit()

        result = scrape_pending_articles(db_session)

        assert result['scraped'] == 0
        assert result['errors'] == 0
