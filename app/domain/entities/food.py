from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FoodMetadata:
    food: str
    available_markets: list[str]
    available_price_types: list[str]


@dataclass(frozen=True, slots=True)
class FoodPriceSnapshot:
    item: str
    price: float
