from __future__ import annotations

import pandas as pd

from app.core.exceptions import (
    FoodNotFoundError,
    InvalidTimeRangeError,
    MarketNotFoundError,
    PriceTypeNotFoundError,
)
from app.core.text import normalize_key
from app.domain.interfaces.repository import DatasetRepository


TIME_RANGE_TO_OFFSET = {
    "7d": pd.DateOffset(days=7),
    "30d": pd.DateOffset(days=30),
    "3m": pd.DateOffset(months=3),
    "6m": pd.DateOffset(months=6),
    "1y": pd.DateOffset(years=1),
    "2y": pd.DateOffset(years=2),
    "all": None,
}


def resolve_food_name(repository: DatasetRepository, food_name: str) -> str:
    foods = repository.get_foods()
    matched = _match_value(foods, food_name)
    if matched is None:
        raise FoodNotFoundError(f"{food_name} not found")
    return matched


def resolve_market_name(repository: DatasetRepository, market: str) -> str:
    markets = repository.get_markets()
    matched = _match_value(markets, market)
    if matched is None:
        raise MarketNotFoundError(f"{market} not found")
    return matched


def resolve_price_type(repository: DatasetRepository, price_type: str) -> str:
    price_types = repository.get_price_types()
    matched = _match_value(price_types, price_type)
    if matched is None:
        raise PriceTypeNotFoundError(f"{price_type} not found")
    return matched


def filter_by_time_range(dataframe: pd.DataFrame, time_range: str) -> pd.DataFrame:
    if time_range not in TIME_RANGE_TO_OFFSET:
        raise InvalidTimeRangeError(f"Unsupported time range: {time_range}")

    if dataframe.empty or time_range == "all":
        return dataframe.copy()

    latest_date = dataframe["date"].max()
    offset = TIME_RANGE_TO_OFFSET[time_range]
    assert offset is not None
    start_date = latest_date - offset
    return dataframe.loc[dataframe["date"] >= start_date].copy()


def _match_value(values: list[str], candidate: str) -> str | None:
    normalized_candidate = normalize_key(candidate)
    for value in values:
        if normalize_key(value) == normalized_candidate:
            return value
    return None
