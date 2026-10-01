"""Technician matching for assessment (Scenario 5) and repair dispatch (Scenario 8)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class Technician:
    name: str
    trades: list[str]
    service_areas: list[str]
    available_days: list[str]
    current_jobs: int = 0
    max_daily_jobs: int = 6
    rating: float = 0.0
    active: bool = True
    notes: list[str] = field(default_factory=list)


def _norm(values: Iterable[str]) -> set[str]:
    return {v.strip().lower() for v in values if v and v.strip()}


def eligible(tech: Technician, trade: str, area: str, preferred_days: Iterable[str]) -> bool:
    if not tech.active or tech.current_jobs >= tech.max_daily_jobs:
        return False
    if trade.lower() not in _norm(tech.trades) and "general maintenance" not in _norm(tech.trades):
        return False
    if area.lower() not in _norm(tech.service_areas):
        return False
    days = _norm(preferred_days)
    return not days or bool(days & _norm(tech.available_days))


def rank_technicians(techs: Iterable[Technician], *, trade: str, area: str,
                     preferred_days: Iterable[str] = (), preferred_technician: str | None = None) -> list[Technician]:
    """Return eligible technicians, best first.

    Order: the preferred technician (e.g. whoever did the assessment), then an
    exact trade match over a general-maintenance fallback, then lightest
    workload, then highest rating.
    """
    days = list(preferred_days)
    pool = [t for t in techs if eligible(t, trade, area, days)]

    def key(t: Technician):
        return (
            0 if preferred_technician and t.name == preferred_technician else 1,
            0 if trade.lower() in _norm(t.trades) else 1,
            t.current_jobs,
            -t.rating,
        )

    return sorted(pool, key=key)
