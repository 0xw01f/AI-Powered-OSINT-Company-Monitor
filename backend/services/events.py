"""Event detection and classification service."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from backend.database.models import Article, Entity, Event, EventType

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


_EVENT_KEYWORDS: dict[EventType, list[str]] = {
    EventType.ACQUISITION: [
        'acquires', 'acquisition', 'acquired', 'buys', 'bought',
        'purchase of', 'takeover', 'buys out', 'acquiring',
    ],
    EventType.PARTNERSHIP: [
        'partnership', 'partners with', 'collaborates with',
        'alliance', 'teams up with', 'joins forces', 'strategic partnership',
        'signs deal with', 'cooperation agreement',
    ],
    EventType.FUNDING: [
        'raises', 'funding', 'series', 'investment', 'valued at',
        'venture capital', 'seed round', 'ipo', 'initial public offering',
        'million funding', 'billion funding', 'financing round',
    ],
    EventType.CYBER_INCIDENT: [
        'vulnerability', 'breach', 'hack', 'ransomware', 'zero-day',
        'exploit', 'cyberattack', 'data leak', 'patches', 'security flaw',
        'malware', 'phishing', 'ddos', 'cve-', 'security update',
    ],
    EventType.LAWSUIT: [
        'sues', 'lawsuit', 'litigation', 'court', 'settlement',
        'files suit', 'antitrust', 'fine', 'penalty', 'regulatory action',
        'investigation', 'charged with',
    ],
    EventType.PRODUCT_LAUNCH: [
        'launches', 'announces', 'unveils', 'releases', 'introduces',
        'debuts', 'rolls out', 'new product', 'now available',
    ],
    EventType.HIRING: [
        'hires', 'appoints', 'joins as', 'new ceo', 'new cto',
        'recruits', 'named', 'new chief', 'executive appointment',
    ],
    EventType.LAYOFFS: [
        'layoffs', 'cuts jobs', 'workforce reduction', 'fires',
        'terminates', 'downsizing', 'job cuts', 'staff reduction',
        'cuts', 'eliminates',
    ],
}

# Compile regexes for efficiency
_EVENT_PATTERNS: dict[EventType, list[re.Pattern[str]]] = {
    event_type: [re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE) for kw in keywords]
    for event_type, keywords in _EVENT_KEYWORDS.items()
}


_HIGH_CONFIDENCE_TITLE_MATCH = [
    EventType.CYBER_INCIDENT,
    EventType.LAWSUIT,
    EventType.ACQUISITION,
]


def classify_event(text: str | None, title: str | None) -> EventType | None:
    """Classify an article into an event type based on title and content.

    Returns the most specific event type found, or None if no match.
    """
    combined = f'{title or ""} {text or ""}'
    if not combined.strip():
        return None

    best_type: EventType | None = None
    best_score = 0

    for event_type, patterns in _EVENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = len(pattern.findall(combined))
            score += matches

        if score > best_score:
            best_score = score
            best_type = event_type

    return best_type


def detect_events_for_article(db: Session, article: Article) -> list[Event]:
    """Detect business events for a given article.

    Uses NER-companies found in the article and matches event patterns.
    Returns created Event objects (not yet committed).
    """
    event_type = classify_event(article.content, article.title)
    if event_type is None:
        return []

    # Find companies mentioned in this article via NER
    companies = (
        db.query(Entity.name)
        .filter_by(article_id=article.id)
        .filter(Entity.type == 'Company')
        .distinct()
        .all()
    )

    if not companies:
        # Fallback: try to extract company from title using simple heuristics
        # (first word that looks like a proper noun)
        return []

    events: list[Event] = []
    for (company_name,) in companies:
        # Determine confidence based on where the keyword appeared
        confidence = 'medium'
        if article.title:
            title_event = classify_event(None, article.title)
            if title_event == event_type and event_type in _HIGH_CONFIDENCE_TITLE_MATCH:
                confidence = 'high'

        events.append(Event(
            article_id=article.id,
            company_name=company_name,
            event_type=event_type,
            confidence=confidence,
        ))

    return events


def get_events(
    db: Session,
    company: str | None = None,
    event_type: EventType | None = None,
    limit: int = 50,
) -> list[Event]:
    """List events with optional filters."""
    query = db.query(Event).order_by(Event.created_at.desc())
    if company:
        query = query.filter(Event.company_name.ilike(company))
    if event_type:
        query = query.filter_by(event_type=event_type)
    return query.limit(limit).all()


def get_event_summary(db: Session) -> dict[str, int]:
    """Return count of events per type."""
    from sqlalchemy import func

    rows = (
        db.query(Event.event_type, func.count(Event.id))
        .group_by(Event.event_type)
        .all()
    )
    return {row[0].value: row[1] for row in rows}
