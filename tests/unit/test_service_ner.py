"""Unit tests for the NER service."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import backend.services.ner
from backend.database.base import Base
from backend.database.models import Article, ArticleStatus, Entity
from backend.services.ner import analyze_articles


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


class TestAnalyzeArticles:
    """Test suite for analyze_articles service."""

    def test_analyzes_scraped_articles(
        self,
        db_session: Session,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Successful analysis should insert entities and update status."""
        def mock_extract(text: str, language: str = 'en') -> list[dict[str, str]]:
            return [{'name': 'Google', 'type': 'Company'}]

        monkeypatch.setitem(
            backend.services.ner._EXTRACTORS,
            'hybrid',
            mock_extract,
        )

        article = Article(
            title='Tech News',
            url='http://example.com/tech',
            content='Google announced new AI features.',
            status=ArticleStatus.SCRAPED,
            language='en',
        )
        db_session.add(article)
        db_session.commit()

        result = analyze_articles(db_session, method='hybrid')

        assert result['analyzed'] == 1
        assert result['entities_found'] == 1
        assert article.status == ArticleStatus.ANALYZED
        assert article.analysis is not None
        assert article.analysis['ner_method'] == 'hybrid'

        entities = db_session.query(Entity).filter_by(article_id=article.id).all()
        assert len(entities) == 1
        assert entities[0].name == 'Google'
        assert entities[0].type == 'Company'

    def test_deduplicates_entities(self, db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
        """Duplicate entities should not be inserted twice."""
        def mock_extract(text: str, language: str = 'en') -> list[dict[str, str]]:
            return [
                {'name': 'Meta', 'type': 'Company'},
                {'name': 'Meta', 'type': 'Company'},
            ]

        monkeypatch.setitem(
            backend.services.ner._EXTRACTORS,
            'hybrid',
            mock_extract,
        )

        article = Article(
            title='Social Media',
            url='http://example.com/social',
            content='Meta and Meta again.',
            status=ArticleStatus.SCRAPED,
        )
        db_session.add(article)
        db_session.commit()

        result = analyze_articles(db_session)

        assert result['entities_found'] == 1
        entities = db_session.query(Entity).filter_by(article_id=article.id).all()
        assert len(entities) == 1

    def test_ignores_non_scraped(self, db_session: Session, monkeypatch: pytest.MonkeyPatch) -> None:
        """Articles not in SCRAPED status should be ignored."""
        def mock_extract(text: str, language: str = 'en') -> list[dict[str, str]]:
            return [{'name': 'Amazon', 'type': 'Company'}]

        monkeypatch.setitem(
            backend.services.ner._EXTRACTORS,
            'hybrid',
            mock_extract,
        )

        article = Article(
            title='Pending',
            url='http://example.com/pending',
            status=ArticleStatus.PENDING,
        )
        db_session.add(article)
        db_session.commit()

        result = analyze_articles(db_session)

        assert result['analyzed'] == 0
        assert result['entities_found'] == 0

    def test_invalid_method_raises(self, db_session: Session) -> None:
        """An unknown method should raise ValueError."""
        with pytest.raises(ValueError, match='Unknown NER method'):
            analyze_articles(db_session, method='invalid')
