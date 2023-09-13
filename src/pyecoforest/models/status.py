"""Model for the Ecoforest stove status."""
from __future__ import annotations

from dataclasses import dataclass

from .state import State


@dataclass
class Status:
    """Model for the Ecoforest stove status."""

    on: bool
    state: State
    power: int
    temperature: float
