# AI-Powered OSINT Company Monitor

A platform that automatically monitors a company and produces actionable summaries from public data.

## Stack

| Tool | Purpose |
| --- | --- |
| [uv](https://docs.astral.sh/uv/) | Fast dependency & virtualenv management |
| [FastAPI](https://fastapi.tiangolo.com/) | Web framework |
| [SQLAlchemy](https://www.sqlalchemy.org/) | ORM |
| [PostgreSQL](https://www.postgresql.org/) | Database |
| [Playwright](https://playwright.dev/python/) | Web scraping |
| [OpenAI](https://platform.openai.com/) | AI analysis |
| [pandas](https://pandas.pydata.org/) | Data manipulation |
| [feedparser](https://pypi.org/project/feedparser/) | RSS feed parsing |
| [Ruff](https://docs.astral.sh/ruff/) | Linter + formatter |
| [Mypy](https://mypy.readthedocs.io/) | Static type checking |
| [Pytest](https://docs.pytest.org/) | Test runner |
| [pre-commit](https://pre-commit.com/) | Git hooks orchestration |

## Requirements

- Python **3.13+**
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker & Docker Compose (for PostgreSQL)

## Getting started

```sh
# 1. Start PostgreSQL
docker compose up -d

# 2. Install dependencies and dev tools
uv sync

# 3. Install git hooks
uv run pre-commit install
```

## Daily commands

```sh
uv run fastapi dev backend/main.py   # run the API
uv run ruff check .                  # lint
uv run ruff format .                 # format
uv run mypy                          # type-check
uv run pytest                        # tests
uv run pytest --cov                  # tests with coverage
```

## Layout

```text
.
├── backend/
│   ├── app/           # source package
│   ├── scrapers/      # web scrapers
│   ├── services/      # business logic
│   ├── database/      # DB models & sessions
│   └── main.py        # FastAPI entry point
├── frontend/          # dashboard (future)
├── tests/
│   └── unit/
├── docker-compose.yml # PostgreSQL service
├── pyproject.toml
└── uv.lock
```

## Commit convention

Commits must follow [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat(scope): add new capability
fix: correct off-by-one in parser
chore: bump dependencies
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

## License

[GPL-3.0-or-later](LICENSE)
