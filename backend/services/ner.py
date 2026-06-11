"""NER service orchestrating entity extraction from scraped articles."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from backend.database.models import Article, ArticleStatus, Entity
from backend.nlp import extract_entities_gliner, extract_entities_hybrid, extract_entities_spacy
from backend.services.events import detect_events_for_article

if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_EXTRACTORS: dict[str, Callable[..., list[dict[str, str]]]] = {
    'spacy': extract_entities_spacy,
    'gliner': extract_entities_gliner,
    'hybrid': extract_entities_hybrid,
}


def analyze_articles(
    db: Session,
    method: str = 'hybrid',
    batch_size: int = 10,
) -> dict[str, int | float]:
    """Extract entities from SCRAPED articles and store them.

    Args:
        db: SQLAlchemy session.
        method: NER method to use ('spacy', 'gliner', or 'hybrid').
        batch_size: Maximum articles to process.

    Returns:
        Dict with 'analyzed', 'entities_found', and 'duration_ms'.
    """
    extractor = _EXTRACTORS.get(method)
    if extractor is None:
        raise ValueError(f'Unknown NER method: {method}. Choose from {list(_EXTRACTORS)}')

    articles = (
        db.query(Article)
        .filter_by(status=ArticleStatus.SCRAPED)
        .limit(batch_size)
        .all()
    )

    total_entities = 0
    start_time = time.perf_counter()

    for article in articles:
        if not article.content:
            continue

        try:
            entities = extractor(article.content, language=article.language or 'en')
        except Exception:
            logger.exception('NER failed for article %d', article.id)
            continue

        for ent in entities:
            existing = (
                db.query(Entity)
                .filter_by(
                    article_id=article.id,
                    name=ent['name'],
                    type=ent['type'],
                )
                .first()
            )
            if existing is None:
                db.add(Entity(
                    article_id=article.id,
                    name=ent['name'],
                    type=ent['type'],
                ))
                total_entities += 1

        article.status = ArticleStatus.ANALYZED
        article.analysis = {
            'ner_method': method,
            'entities_count': len(entities),
        }

        # Detect business events for this article
        try:
            events = detect_events_for_article(db, article)
            for event in events:
                db.add(event)
        except Exception:
            logger.exception('Event detection failed for article %d', article.id)

    db.commit()
    duration = (time.perf_counter() - start_time) * 1000

    return {
        'analyzed': len(articles),
        'entities_found': total_entities,
        'duration_ms': round(duration, 2),
    }
