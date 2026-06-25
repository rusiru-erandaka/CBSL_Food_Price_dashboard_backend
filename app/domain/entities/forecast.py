from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class ForecastPoint:
    date: date
    predicted_price: float


@dataclass(frozen=True, slots=True)
class FoodForecast:
    food: str
    market: str
    price_type: str
    model: str
    forecast: list[ForecastPoint]


@dataclass(frozen=True, slots=True)
class FoodStatistics:
    food: str
    market: str
    price_type: str
    min_price: float
    max_price: float
    avg_price: float
    current_price: float
    price_change_percent: float
    volatility: float
