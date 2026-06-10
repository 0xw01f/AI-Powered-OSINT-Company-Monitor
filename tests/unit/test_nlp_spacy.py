"""Unit tests for spaCy NER extractor."""

from __future__ import annotations

from backend.nlp.spacy_ner import extract_entities


class TestSpacyNer:
    """Test suite for spaCy entity extraction."""

    def test_extracts_company_from_english_text(self) -> None:
        """spaCy should detect ORG entities in English."""
        text = 'Apple Inc. is planning to open a new office in Berlin.'
        entities = extract_entities(text, language='en')
        names = {e['name'] for e in entities}
        assert 'Apple Inc.' in names or 'Apple' in names

    def test_extracts_person(self) -> None:
        """spaCy should detect PERSON entities."""
        text = 'Elon Musk announced the new Tesla model yesterday.'
        entities = extract_entities(text, language='en')
        types = {e['type'] for e in entities}
        assert 'Person' in types

    def test_empty_text_returns_empty_list(self) -> None:
        """Empty input should return an empty list."""
        assert extract_entities('', language='en') == []
        assert extract_entities('   ', language='en') == []

    def test_french_text(self) -> None:
        """spaCy should detect ORG entities in French."""
        text = 'TotalEnergies a annoncé un nouveau projet à Paris.'
        entities = extract_entities(text, language='fr')
        names = {e['name'] for e in entities}
        assert 'TotalEnergies' in names

    def test_deduplicates_entities(self) -> None:
        """Duplicate entities should appear only once."""
        text = 'Apple is great. Apple is innovative. Apple makes phones.'
        entities = extract_entities(text, language='en')
        apple_count = sum(1 for e in entities if 'Apple' in e['name'])
        assert apple_count == 1
