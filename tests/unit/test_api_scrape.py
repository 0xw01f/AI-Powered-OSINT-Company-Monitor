"""Unit tests for the scrape API endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> TestClient:
    """Return a TestClient for the FastAPI app."""
    return TestClient(app)


class TestScrapeEndpoint:
    """Test suite for POST /collect/scrape."""

    def test_scrape_endpoint_returns_summary(self, client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
        """Endpoint should return scraped and error counts."""
        def mock_scrape_pending(db: object, batch_size: int = 10) -> dict[str, int]:
            return {'scraped': 3, 'errors': 1}

        monkeypatch.setattr(
            'backend.api.routes.scrape_pending_articles',
            mock_scrape_pending,
        )

        response = client.post('/collect/scrape?batch_size=5')

        assert response.status_code == 200
        assert response.json() == {
            'status': 'success',
            'scraped': 3,
            'errors': 1,
        }

    def test_scrape_endpoint_default_batch_size(self, client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
        """Default batch_size should be 10 when not provided."""
        captured: dict[str, int] = {}

        def mock_scrape_pending(db: object, batch_size: int = 10) -> dict[str, int]:
            captured['batch_size'] = batch_size
            return {'scraped': 0, 'errors': 0}

        monkeypatch.setattr(
            'backend.api.routes.scrape_pending_articles',
            mock_scrape_pending,
        )

        response = client.post('/collect/scrape')

        assert response.status_code == 200
        assert captured['batch_size'] == 10
