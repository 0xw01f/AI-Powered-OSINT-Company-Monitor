"""Unit tests for the background scheduler."""

from __future__ import annotations

from backend.scheduler import get_scheduler_status, start_scheduler, stop_scheduler


class TestScheduler:
    """Test suite for the background scheduler."""

    def test_start_and_stop_scheduler(self) -> None:
        """Scheduler should start and stop cleanly."""
        start_scheduler()
        status = get_scheduler_status()
        assert status['running'] is True
        assert len(status['jobs']) == 3
        job_ids = {job['id'] for job in status['jobs']}
        assert job_ids == {'rss', 'scrape', 'ner'}
        stop_scheduler()
        status = get_scheduler_status()
        assert status['running'] is False
        assert status['jobs'] == []

    def test_status_when_not_started(self) -> None:
        """Status should report not running before start."""
        stop_scheduler()
        status = get_scheduler_status()
        assert status['running'] is False
        assert status['jobs'] == []
