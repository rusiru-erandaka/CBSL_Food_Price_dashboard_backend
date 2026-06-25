from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class TrendPoint:
    date: date
    price: float


@dataclass(frozen=True, slots=True)
class FoodTrend:
    food: str
    market: str
    price_type: str
    points: list[TrendPoint]
