"""Unit tests for the monitor API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> TestClient:
    """Return a TestClient for the FastAPI app."""
    return TestClient(app)


class TestMonitorSearch:
    """Test suite for GET /collect/monitor/search."""

    def test_search_endpoint(self, client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
        """Endpoint should return article list."""
        def mock_search(db: object, name: str, limit: int = 20) -> list[object]:
            return [type('Article', (), {'id': 1, 'title': 'News', 'url': 'http://x', 'source': 'X', 'published_at': None})]

        monkeypatch.setattr('backend.api.routes.search_articles_by_company', mock_search)

        response = client.get('/collect/monitor/search?name=Tesla')

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == 'News'


class TestMonitorWatch:
    """Test suite for POST /collect/monitor/watch."""

    def test_watch_endpoint(self, client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
        """Endpoint should add company to watchlist."""
        def mock_add(db: object, name: str) -> object:
            return type('Company', (), {'name': name})()

        monkeypatch.setattr('backend.api.routes.add_monitored_company', mock_add)

        response = client.post('/collect/monitor/watch?name=Apple')

        assert response.status_code == 200
        assert response.json()['status'] == 'added'

    def test_watch_duplicate(self, client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
        """Endpoint should report duplicate."""
        def mock_add(db: object, name: str) -> None:
            return None

        monkeypatch.setattr('backend.api.routes.add_monitored_company', mock_add)

        response = client.post('/collect/monitor/watch?name=Apple')

        assert response.status_code == 200
        assert response.json()['status'] == 'already_exists'


class TestMonitorUnwatch:
    """Test suite for DELETE /collect/monitor/watch."""

    def test_unwatch_endpoint(self, client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
        """Endpoint should remove company from watchlist."""
        def mock_remove(db: object, name: str) -> bool:
            return True

        monkeypatch.setattr('backend.api.routes.remove_monitored_company', mock_remove)

        response = client.delete('/collect/monitor/watch?name=Apple')

        assert response.status_code == 200
        assert response.json()['status'] == 'removed'


class TestMonitorWatched:
    """Test suite for GET /collect/monitor/watched."""

    def test_watched_endpoint(self, client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
        """Endpoint should return watched companies."""
        def mock_list(db: object) -> list[object]:
            return [type('Company', (), {'name': 'Tesla'})()]

        monkeypatch.setattr('backend.api.routes.list_monitored_companies', mock_list)

        response = client.get('/collect/monitor/watched')

        assert response.status_code == 200
        assert response.json() == [{'name': 'Tesla'}]


class TestMonitorAlerts:
    """Test suite for GET /collect/monitor/alerts."""

    def test_alerts_endpoint(self, client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
        """Endpoint should return alerts."""
        def mock_alerts(db: object, hours: int = 24, limit: int = 50) -> list[object]:
            return [type('Article', (), {'id': 1, 'title': 'Alert', 'url': 'http://x', 'source': 'X', 'published_at': None})]

        monkeypatch.setattr('backend.api.routes.get_alerts', mock_alerts)

        response = client.get('/collect/monitor/alerts?hours=12')

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == 'Alert'
