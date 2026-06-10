"""Unit tests for the analyze API endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> TestClient:
    """Return a TestClient for the FastAPI app."""
    return TestClient(app)


class TestAnalyzeEndpoint:
    """Test suite for POST /collect/analyze."""

    def test_analyze_endpoint(self, client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
        """Endpoint should return analysis summary."""
        def mock_analyze(db: object, method: str = 'hybrid', batch_size: int = 10) -> dict[str, object]:
            return {'analyzed': 2, 'entities_found': 5, 'duration_ms': 230.5}

        monkeypatch.setattr('backend.api.routes.analyze_articles', mock_analyze)

        response = client.post('/collect/analyze?method=hybrid&batch_size=5')

        assert response.status_code == 200
        assert response.json() == {
            'status': 'success',
            'analyzed': 2,
            'entities_found': 5,
            'duration_ms': 230.5,
        }


class TestBenchmarkEndpoint:
    """Test suite for POST /collect/benchmark."""

    def test_benchmark_endpoint(self, client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
        """Endpoint should return benchmark results."""
        def mock_benchmark(text: str, language: str = 'en') -> dict[str, object]:
            return {
                'spacy': {'count': 2, 'duration_ms': 12.0},
                'gliner': {'count': 3, 'duration_ms': 45.0},
                'hybrid': {'count': 3, 'duration_ms': 50.0},
            }

        monkeypatch.setattr('backend.api.routes.benchmark_text', mock_benchmark)

        response = client.post('/collect/benchmark?text=Apple%20is%20great&language=en')

        assert response.status_code == 200
        data = response.json()
        assert data['spacy']['count'] == 2
        assert data['gliner']['count'] == 3
        assert data['hybrid']['count'] == 3
