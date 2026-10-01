"""Status lifecycle guard. Scenarios call can_transition() before writing a new status."""

from __future__ import annotations

from .config import status_lifecycle


class InvalidTransition(ValueError):
    pass


def statuses() -> list[str]:
    return list(status_lifecycle()["statuses"])


def allowed_next(current: str) -> list[str]:
    transitions = status_lifecycle()["transitions"]
    if current not in transitions:
        raise KeyError(f"Unknown status: {current!r}")
    return list(transitions[current])


def can_transition(current: str, new: str) -> bool:
    return new in allowed_next(current)


def transition(current: str, new: str) -> str:
    if not can_transition(current, new):
        raise InvalidTransition(f"{current!r} -> {new!r} is not allowed; expected one of {allowed_next(current)}")
    return new
