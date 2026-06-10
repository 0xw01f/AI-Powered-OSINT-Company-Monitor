"""Configuration loader for RSS sources."""

from __future__ import annotations

import csv
import pathlib
from dataclasses import dataclass
from typing import Any

import yaml


@dataclass
class SourceConfig:
    """RSS source configuration."""

    name: str
    url: str
    category: str
    language: str


def _load_csv(path: pathlib.Path) -> list[SourceConfig]:
    """Load source configurations from CSV."""
    sources: list[SourceConfig] = []
    with open(path, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sources.append(
                SourceConfig(
                    name=row['name'],
                    url=row['url'],
                    category=row.get('category') or 'general',
                    language=row.get('language') or 'en',
                ),
            )
    return sources


def _load_yaml(path: pathlib.Path) -> list[SourceConfig]:
    """Load source configurations from YAML."""
    with open(path, encoding='utf-8') as f:
        data: dict[str, Any] = yaml.safe_load(f)
    return [SourceConfig(**src) for src in data.get('sources', [])]


def load_sources(config_path: pathlib.Path | None = None) -> list[SourceConfig]:
    """Load RSS source configurations from CSV or YAML."""
    if config_path is None:
        csv_path = pathlib.Path(__file__).parent / 'sources.csv'
        if csv_path.exists():
            return _load_csv(csv_path)
        config_path = pathlib.Path(__file__).parent / 'sources.yaml'

    if config_path.suffix == '.csv':
        return _load_csv(config_path)

    return _load_yaml(config_path)
