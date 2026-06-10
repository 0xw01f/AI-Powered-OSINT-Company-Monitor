"""Benchmark utility comparing NER methods."""

from __future__ import annotations

import time
from collections.abc import Callable  # noqa: TC003

from backend.nlp.gliner_ner import extract_entities as extract_gliner
from backend.nlp.hybrid_ner import extract_entities as extract_hybrid
from backend.nlp.spacy_ner import extract_entities as extract_spacy


def _timed(func: Callable[[str], list[dict[str, str]]], text: str) -> tuple[list[dict[str, str]], float]:
    """Run a function and return (result, duration_ms)."""
    start = time.perf_counter()
    result = func(text)
    duration = (time.perf_counter() - start) * 1000
    return result, duration


def benchmark_text(text: str, language: str = 'en') -> dict[str, dict[str, object]]:
    """Compare spacy, gliner, and hybrid on a single text.

    Returns a dict mapping method name to metrics.
    """
    spacy_entities, spacy_time = _timed(lambda t: extract_spacy(t, language), text)
    gliner_entities, gliner_time = _timed(extract_gliner, text)
    hybrid_entities, hybrid_time = _timed(lambda t: extract_hybrid(t, language), text)

    return {
        'spacy': {
            'entities': spacy_entities,
            'count': len(spacy_entities),
            'duration_ms': round(spacy_time, 2),
        },
        'gliner': {
            'entities': gliner_entities,
            'count': len(gliner_entities),
            'duration_ms': round(gliner_time, 2),
        },
        'hybrid': {
            'entities': hybrid_entities,
            'count': len(hybrid_entities),
            'duration_ms': round(hybrid_time, 2),
        },
    }
