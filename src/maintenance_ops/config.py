"""Load business rules and the status lifecycle from the config/ folder."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).resolve().parents[2] / "config"


def _load(name: str, config_dir: Path | None = None) -> dict[str, Any]:
    path = (config_dir or CONFIG_DIR) / name
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@lru_cache(maxsize=None)
def business_rules() -> dict[str, Any]:
    return _load("business_rules.yaml")


@lru_cache(maxsize=None)
def status_lifecycle() -> dict[str, Any]:
    return _load("status_lifecycle.yaml")
