"""Configuration loader for RSS sources."""

from __future__ import annotations

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


def load_sources(config_path: pathlib.Path | None = None) -> list[SourceConfig]:
    """Load RSS source configurations from YAML."""
    if config_path is None:
        config_path = pathlib.Path(__file__).parent / 'sources.yaml'
    with open(config_path, encoding='utf-8') as f:
        data: dict[str, Any] = yaml.safe_load(f)
    return [
        SourceConfig(**src) for src in data.get('sources', [])
    ]
