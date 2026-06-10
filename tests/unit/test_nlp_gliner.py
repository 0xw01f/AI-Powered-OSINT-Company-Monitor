"""Unit tests for GLiNER NER extractor."""

from __future__ import annotations

import pytest

from backend.nlp import gliner_ner


class TestGlinerNer:
    """Test suite for GLiNER entity extraction."""

    def test_extracts_company_with_mock(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """GLiNER should return mocked entities."""

        class _MockModel:
            def predict_entities(
                self,
                text: str,
                labels: list[str],
                threshold: float,
            ) -> list[dict[str, object]]:
                return [{'text': 'Microsoft', 'label': 'Company', 'score': 0.95}]

        monkeypatch.setattr(
            gliner_ner,
            '_GLINER_MODEL',
            _MockModel(),
        )
        entities = gliner_ner.extract_entities('Microsoft is hiring.')
        assert len(entities) == 1
        assert entities[0]['name'] == 'Microsoft'
        assert entities[0]['type'] == 'Company'

    def test_empty_text_returns_empty_list(self) -> None:
        """Empty input should return an empty list."""
        assert gliner_ner.extract_entities('') == []
        assert gliner_ner.extract_entities('   ') == []
