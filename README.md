# AI-Powered OSINT Company Monitor

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![spaCy](https://img.shields.io/badge/spaCy-3.8-09A3D5?logo=spacy&logoColor=white)](https://spacy.io/)
[![GLiNER](https://img.shields.io/badge/GLiNER-NER-FF6F00?logo=huggingface&logoColor=white)](https://github.com/urchade/GLiNER)
[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?logo=playwright&logoColor=white)](https://playwright.dev/python/)
[![APScheduler](https://img.shields.io/badge/APScheduler-3.11-9cf)](https://apscheduler.readthedocs.io/)
[![Ruff](https://img.shields.io/badge/Ruff-261230?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)
[![Mypy](https://img.shields.io/badge/mypy-strict-2A6DB2?logo=python&logoColor=white)](https://mypy.readthedocs.io/)
[![Pytest](https://img.shields.io/badge/pytest-79+_tests-0A9EDC?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-GPL--3.0-orange)](LICENSE)

An automated OSINT platform that monitors companies through public RSS feeds and web sources, extracts named entities (companies, products, technologies, people…), and alerts on mentions of watched companies.

## What it does

1. **RSS Collection** — Reads 360+ pre-configured RSS sources (security, regulation, tech, finance, press…), filters by priority, and stores articles in PostgreSQL.
2. **Web Scraping** — For articles without full content, Playwright + BeautifulSoup extracts the article body (`<article>`, `<main>`, or full body fallback).
3. **NER (Entity Extraction)** — Hybrid pipeline:
   - **spaCy** filters relevant paragraphs (~5 ms)
   - **GLiNER** zero-shot NER refines entity types (~150 ms)
   - Combined result: ~50 ms with custom labels (Company, Product, Technology, Person, Financial Amount, Location)
4. **Monitoring** — Search articles by company, maintain a watchlist, and get recent alerts.
5. **Scheduler** — APScheduler runs RSS collection (every 30 min), scraping (15 min), and NER analysis (15 min) automatically.

## Stack

| Tool | Purpose |
|------|---------|
| [uv](https://docs.astral.sh/uv/) | Dependency & virtualenv management |
| [FastAPI](https://fastapi.tiangolo.com/) | Web API |
| [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | ORM |
| [PostgreSQL 16](https://www.postgresql.org/) | Database |
| [Playwright](https://playwright.dev/python/) | Headless web scraping |
| [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) | HTML parsing |
| [spaCy](https://spacy.io/) + [GLiNER](https://github.com/urchade/GLiNER) | Named Entity Recognition |
| [APScheduler](https://apscheduler.readthedocs.io/) | Background job scheduler |
| [feedparser](https://pypi.org/project/feedparser/) | RSS/Atom parsing |
| [Ruff](https://docs.astral.sh/ruff/) | Linter + formatter |
| [Mypy](https://mypy.readthedocs.io/) | Static type checking (strict) |
| [Pytest](https://docs.pytest.org/) | Test runner (60+ tests) |

## Requirements

- **Python 3.13+**
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** (package manager)
- **Docker & Docker Compose** (for PostgreSQL)
- **Git Bash / WSL / Linux/macOS** (for shell scripts)

## Quick start

```bash
# 1. Clone
git clone <repo-url>
cd AI-Powered-OSINT-Company-Monitor

# 2. Start PostgreSQL
docker compose up -d

# 3. Install Python dependencies
uv sync

# 4. Install spaCy language models (required for NER)
uv run python -m spacy download en_core_web_sm
uv run python -m spacy download fr_core_news_sm

# 5. Start the API server
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

The first startup will:
- Create database tables automatically
- Import 360 sources from `backend/config/sources.csv`
- Start the background scheduler
- Download the GLiNER model from HuggingFace (first NER call only, ~500 MB, cached afterwards)

## Test the API

With the server running, open another terminal and run:

```bash
# Health check
curl http://127.0.0.1:8000/health
# → {"status":"ok","database":"connected"}

# List high-priority active sources (security & regulation)
curl "http://127.0.0.1:8000/sources/?active_only=true&min_priority=95"

# Trigger RSS collection on top-5 priority sources
curl -X POST "http://127.0.0.1:8000/collect/rss?max_sources=5&limit_per_source=10"
# → {"status":"success","inserted":N,"skipped":M}

# Trigger scraping for pending articles
curl -X POST "http://127.0.0.1:8000/collect/scrape?batch_size=10"

# Trigger NER analysis (hybrid = spaCy + GLiNER)
curl -X POST "http://127.0.0.1:8000/collect/analyze?method=hybrid&batch_size=10"

# Benchmark NER methods on a sample text
curl -X POST "http://127.0.0.1:8000/collect/benchmark" \
  -H "Content-Type: application/json" \
  -d '{"text": "Apple Inc. announced a partnership with OpenAI in San Francisco.", "language": "en"}'

# Watchlist: add a company
curl -X POST "http://127.0.0.1:8000/collect/monitor/watch?name=Apple"

# Watchlist: list watched companies
curl http://127.0.0.1:8000/collect/monitor/watched

# Search articles mentioning a company
curl "http://127.0.0.1:8000/collect/monitor/search?name=Apple&limit=10"

# Get recent alerts (articles mentioning watched companies, last 24h)
curl "http://127.0.0.1:8000/collect/monitor/alerts?hours=24&limit=20"

# Scheduler status
curl http://127.0.0.1:8000/collect/scheduler/status
```

Or run the provided test script:

```bash
bash scripts/test_api.sh
```

## Interactive docs

Once the server is running, open your browser at:

- **Swagger UI** — http://127.0.0.1:8000/docs
- **ReDoc** — http://127.0.0.1:8000/redoc

## Run tests

```bash
# All tests (SQLite in-memory, no Docker required)
uv run pytest

# With coverage report
uv run pytest --cov

# Fast mode (parallel)
uv run pytest -x --timeout=30 -q
```

## Project layout

```text
.
├── backend/
│   ├── main.py              # FastAPI entry point (lifespan: DB init → import sources → scheduler)
│   ├── api/
│   │   ├── routes.py        # /collect/* endpoints (RSS, scrape, analyze, monitor, scheduler)
│   │   └── sources.py       # /sources/* CRUD endpoints
│   ├── collectors/
│   │   └── rss.py           # RSS feed fetching & article deduplication (SHA256 hash)
│   ├── database/
│   │   ├── models.py        # Article, Entity, Source, MonitoredCompany
│   │   └── session.py       # SQLAlchemy engine & SessionLocal
│   ├── nlp/
│   │   ├── spacy_ner.py     # spaCy entity extractor
│   │   ├── gliner_ner.py    # GLiNER zero-shot NER
│   │   ├── hybrid_ner.py    # Hybrid pipeline (GOAT)
│   │   └── benchmark.py     # Comparative benchmark
│   ├── scrapers/
│   │   └── article.py       # Playwright + BeautifulSoup article extractor
│   ├── services/
│   │   ├── sources.py       # CSV import + CRUD logic
│   │   ├── scraper.py       # Scrape pending articles service
│   │   ├── ner.py           # NER analysis service
│   │   └── monitor.py       # Watchlist & alerts
│   ├── scheduler.py         # APScheduler (RSS 30min, scrape 15min, NER 15min)
│   └── config/
│       └── sources.csv      # 360+ RSS sources with metadata
├── tests/
│   └── unit/                # 60 tests covering all layers
├── scripts/
│   └── test_api.sh          # Quick curl-based API smoke tests
├── docker-compose.yml       # PostgreSQL 16
├── pyproject.toml
└── uv.lock
```

## Configuration

No `.env` file is required for local development. Defaults:

| Variable | Default |
|----------|---------|
| `DATABASE_URL` | `postgresql://osint:osint@localhost:5432/osint_monitor` |

If port `8000` is already in use, start the server on another port:

```bash
uv run uvicorn backend.main:app --host 127.0.0.1 --port 8001
```

## Important notes

- **APScheduler** is MVP-only. For production, replace with **Celery + Redis**.
- **First NER call is slow** (~30-60 s) because GLiNER downloads `urchade/gliner_medium-v2.1` from HuggingFace. Subsequent calls use the local cache.
- **RSS collection** is capped to `max_sources=20` by default to avoid timeouts. The scheduler processes sources in priority order.
- **Tests** use an in-memory SQLite database and mock external HTTP calls, so they run offline and fast (~10 s).

## License

[GPL-3.0-or-later](LICENSE)
