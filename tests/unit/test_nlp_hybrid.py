"""Unit tests for hybrid NER extractor."""

from __future__ import annotations

import pytest

from backend.nlp import hybrid_ner


class TestHybridNer:
    """Test suite for hybrid spaCy + GLiNER extraction."""

    def test_falls_back_to_gliner_when_no_spacy_candidates(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """When spaCy finds no ORG/PERSON, hybrid should use GLiNER on full text."""
        monkeypatch.setattr(
            hybrid_ner,
            '_get_candidate_spans',
            lambda _text, _language: [],
        )
        monkeypatch.setattr(
            hybrid_ner,
            'extract_gliner',
            lambda _text: [{'name': 'OpenAI', 'type': 'Company'}],
        )
        entities = hybrid_ner.extract_entities('Some random text.', language='en')
        assert entities == [{'name': 'OpenAI', 'type': 'Company'}]

    def test_uses_gliner_on_candidates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When spaCy finds candidates, hybrid should run GLiNER on those spans."""
        monkeypatch.setattr(
            hybrid_ner,
            '_get_candidate_spans',
            lambda _text, _language: [(0, 20)],
        )
        monkeypatch.setattr(
            hybrid_ner,
            '_merge_spans',
            lambda _spans, _length: ['Tesla is hiring'],
        )
        monkeypatch.setattr(
            hybrid_ner,
            'extract_gliner',
            lambda _text: [{'name': 'Tesla', 'type': 'Company'}],
        )
        entities = hybrid_ner.extract_entities('Tesla is hiring new engineers.', language='en')
        assert any(e['name'] == 'Tesla' and e['type'] == 'Company' for e in entities)

    def test_empty_text_returns_empty_list(self) -> None:
        """Empty input should return an empty list."""
        assert hybrid_ner.extract_entities('') == []
        assert hybrid_ner.extract_entities('   ') == []
