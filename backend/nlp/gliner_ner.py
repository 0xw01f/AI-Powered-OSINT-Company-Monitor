"""GLiNER-based zero-shot entity extraction."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gliner import GLiNER

logger = logging.getLogger(__name__)

_GLINER_MODEL: GLiNER | None = None

_DEFAULT_LABELS = [
    'Company',
    'Product',
    'Person',
    'Technology',
    'Financial Amount',
    'Location',
]


def _load_model() -> GLiNER:
    """Lazy-load the GLiNER model."""
    from gliner import GLiNER as _GLiNER  # noqa: PLC0415

    global _GLINER_MODEL  # noqa: PLW0603
    if _GLINER_MODEL is None:
        logger.info('Loading GLiNER model')
        _GLINER_MODEL = _GLiNER.from_pretrained('urchade/gliner_medium-v2.1')
    return _GLINER_MODEL


def extract_entities(
    text: str,
    labels: list[str] | None = None,
    threshold: float = 0.5,
) -> list[dict[str, str]]:
    """Extract entities from text using GLiNER zero-shot NER.

    Returns a list of dicts with keys 'name' and 'type'.
    """
    if not text or not text.strip():
        return []

    model = _load_model()
    labels = labels or _DEFAULT_LABELS
    predictions = model.predict_entities(text, labels, threshold=threshold)

    entities: list[dict[str, str]] = []
    seen: set[str] = set()

    for pred in predictions:
        key = f'{pred["text"].lower()}|{pred["label"]}'
        if key not in seen:
            seen.add(key)
            entities.append({'name': pred['text'].strip(), 'type': pred['label']})

    return entities
