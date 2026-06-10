"""spaCy-based entity extraction."""

from __future__ import annotations

import logging

import spacy

logger = logging.getLogger(__name__)

_SPACY_MODELS: dict[str, spacy.Language] = {}

_LABEL_MAP = {
    'ORG': 'Organization',
    'PERSON': 'Person',
    'PRODUCT': 'Product',
    'GPE': 'Location',
    'MONEY': 'Financial Amount',
    'WORK_OF_ART': 'Technology',
}


def _load_model(language: str) -> spacy.Language:
    """Lazy-load a spaCy model by language code."""
    model_name = 'fr_core_news_sm' if language.startswith('fr') else 'en_core_web_sm'
    if model_name not in _SPACY_MODELS:
        logger.info('Loading spaCy model %s', model_name)
        _SPACY_MODELS[model_name] = spacy.load(model_name)
    return _SPACY_MODELS[model_name]


def extract_entities(text: str, language: str = 'en') -> list[dict[str, str]]:
    """Extract entities from text using spaCy.

    Returns a list of dicts with keys 'name' and 'type'.
    """
    if not text or not text.strip():
        return []

    nlp = _load_model(language)
    doc = nlp(text)
    entities: list[dict[str, str]] = []
    seen: set[str] = set()

    for ent in doc.ents:
        mapped = _LABEL_MAP.get(ent.label_)
        if mapped is None:
            continue
        key = f'{ent.text.lower()}|{mapped}'
        if key not in seen:
            seen.add(key)
            entities.append({'name': ent.text.strip(), 'type': mapped})

    return entities
