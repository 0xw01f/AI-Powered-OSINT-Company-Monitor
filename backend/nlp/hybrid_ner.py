"""Hybrid NER combining spaCy filtering with GLiNER precision."""

from __future__ import annotations

import logging

from backend.nlp.gliner_ner import extract_entities as extract_gliner
from backend.nlp.spacy_ner import _load_model as load_spacy_model

logger = logging.getLogger(__name__)


def _get_candidate_spans(text: str, language: str) -> list[tuple[int, int]]:
    """Return text spans that contain ORG or PERSON entities from spaCy."""
    nlp = load_spacy_model(language)
    doc = nlp(text)
    spans: list[tuple[int, int]] = []
    for ent in doc.ents:
        if ent.label_ in ('ORG', 'PERSON'):
            spans.append((ent.start_char, ent.end_char))
    return spans


def _merge_spans(spans: list[tuple[int, int]], _text_length: int) -> list[str]:
    """Merge overlapping or adjacent spans and return text chunks."""
    if not spans:
        return []
    spans = sorted(spans)
    merged: list[tuple[int, int]] = [spans[0]]
    for start, end in spans[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end + 100:  # overlap or within 100 chars
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return []


def extract_entities(text: str, language: str = 'en') -> list[dict[str, str]]:
    """Extract entities using hybrid spaCy + GLiNER pipeline.

    spaCy identifies candidate paragraphs with ORG/PERSON; GLiNER
    performs zero-shot NER on those regions for precise typing.
    If no candidates are found, falls back to GLiNER on full text.
    """
    if not text or not text.strip():
        return []

    candidate_spans = _get_candidate_spans(text, language)

    if not candidate_spans:
        logger.debug('No spaCy candidates, falling back to GLiNER on full text')
        return extract_gliner(text)

    chunks = _merge_spans(candidate_spans, len(text))
    if not chunks:
        chunks = [text[s:e] for s, e in candidate_spans]

    entities: list[dict[str, str]] = []
    seen: set[str] = set()

    for chunk in chunks:
        for ent in extract_gliner(chunk):
            key = f'{ent["name"].lower()}|{ent["type"]}'
            if key not in seen:
                seen.add(key)
                entities.append(ent)

    logger.debug('Hybrid extracted %d entities from %d chunks', len(entities), len(chunks))
    return entities
