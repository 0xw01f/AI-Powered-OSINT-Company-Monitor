"""NLP package for entity extraction."""

from backend.nlp.gliner_ner import extract_entities as extract_entities_gliner
from backend.nlp.hybrid_ner import extract_entities as extract_entities_hybrid
from backend.nlp.spacy_ner import extract_entities as extract_entities_spacy

__all__ = [
    'extract_entities_gliner',
    'extract_entities_hybrid',
    'extract_entities_spacy',
]
