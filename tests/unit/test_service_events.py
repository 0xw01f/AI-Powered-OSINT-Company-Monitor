"""Unit tests for event detection service."""

from __future__ import annotations

import pytest

from backend.services.events import classify_event, _EVENT_KEYWORDS
from backend.database.models import EventType


@pytest.mark.parametrize(
    ('title', 'expected'),
    [
        ('Google acquires Fitbit for $2.1 billion', EventType.ACQUISITION),
        ('Apple buys AI startup', EventType.ACQUISITION),
        ('Microsoft partners with OpenAI on cloud deal', EventType.PARTNERSHIP),
        ('Tesla teams up with Panasonic', EventType.PARTNERSHIP),
        ('Stripe raises $600M in Series H', EventType.FUNDING),
        ('Startup valued at $1B after funding round', EventType.FUNDING),
        ('Google patches Chrome zero-day vulnerability', EventType.CYBER_INCIDENT),
        ('Massive data breach at Equifax', EventType.CYBER_INCIDENT),
        ('Epic Games sues Apple over App Store fees', EventType.LAWSUIT),
        ('Regulatory fine hits Meta', EventType.LAWSUIT),
        ('Apple unveils new iPhone 16', EventType.PRODUCT_LAUNCH),
        ('Tesla launches Cybertruck', EventType.PRODUCT_LAUNCH),
        ('Google hires former Intel CEO', EventType.HIRING),
        ('Apple appoints new CFO', EventType.HIRING),
        ('Amazon workforce reduction', EventType.LAYOFFS),
        ('Meta job cuts hit 10,000', EventType.LAYOFFS),
    ],
)
def test_classify_event(title: str, expected: EventType) -> None:
    assert classify_event(title, title) == expected


def test_classify_event_no_match() -> None:
    assert classify_event('Random article about weather', None) is None


def test_classify_event_content_fallback() -> None:
    title = 'Company update'
    content = 'The board announces a strategic partnership with IBM.'
    assert classify_event(content, title) == EventType.PARTNERSHIP


def test_all_event_types_have_keywords() -> None:
    for event_type in EventType:
        if event_type == EventType.UNKNOWN:
            continue
        assert event_type in _EVENT_KEYWORDS
        assert len(_EVENT_KEYWORDS[event_type]) > 0
