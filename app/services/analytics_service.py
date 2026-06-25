from __future__ import annotations

import math

import pandas as pd

from app.core.exceptions import InsufficientDataError
from app.domain.entities.food import FoodPriceSnapshot
from app.domain.entities.forecast import FoodStatistics
from app.domain.interfaces.repository import DatasetRepository
from app.services._utils import (
    filter_by_time_range,
    resolve_food_name,
    resolve_market_name,
    resolve_price_type,
)


class AnalyticsService:
    def __init__(self, repository: DatasetRepository) -> None:
        self._repository = repository

    def get_statistics(
        self,
        food_name: str,
        market: str,
        price_type: str,
        time_range: str,
    ) -> FoodStatistics:
        resolved_food = resolve_food_name(self._repository, food_name)
        resolved_market = resolve_market_name(self._repository, market)
        resolved_price_type = resolve_price_type(self._repository, price_type)

        subset = self._filtered_series(
            food_name=resolved_food,
            market=resolved_market,
            price_type=resolved_price_type,
            time_range=time_range,
        )
        if subset.empty:
            raise InsufficientDataError("No data points available for the requested filters.")

        prices = subset["price"]
        first_price = float(prices.iloc[0])
        current_price = float(prices.iloc[-1])
        change_percent = 0.0
        if first_price != 0:
            change_percent = ((current_price - first_price) / first_price) * 100.0

        return FoodStatistics(
            food=resolved_food,
            market=resolved_market,
            price_type=resolved_price_type,
            min_price=round(float(prices.min()), 2),
            max_price=round(float(prices.max()), 2),
            avg_price=round(float(prices.mean()), 2),
            current_price=round(current_price, 2),
            price_change_percent=round(change_percent, 2),
            volatility=round(float(prices.std(ddof=0)), 2),
        )

    def compare_markets(
        self, food_name: str, price_type: str
    ) -> tuple[str, str, pd.Timestamp | None, list[FoodPriceSnapshot]]:
        resolved_food = resolve_food_name(self._repository, food_name)
        resolved_price_type = resolve_price_type(self._repository, price_type)

        dataset = self._repository.get_dataset()
        subset = dataset.loc[
            (dataset["food"] == resolved_food)
            & (dataset["price_type"] == resolved_price_type)
        ].sort_values("date")
        latest_rows = (
            subset.groupby("market", as_index=False)
            .tail(1)
            .sort_values("market")
            .reset_index(drop=True)
        )

        return (
            resolved_food,
            resolved_price_type,
            latest_rows["date"].max() if not latest_rows.empty else None,
            [
                FoodPriceSnapshot(item=row.market, price=round(float(row.price), 2))
                for row in latest_rows.itertuples(index=False)
            ],
        )

    def compare_foods(
        self, market: str, price_type: str
    ) -> tuple[str, str, pd.Timestamp | None, list[FoodPriceSnapshot]]:
        resolved_market = resolve_market_name(self._repository, market)
        resolved_price_type = resolve_price_type(self._repository, price_type)

        dataset = self._repository.get_dataset()
        subset = dataset.loc[
            (dataset["market"] == resolved_market)
            & (dataset["price_type"] == resolved_price_type)
        ].sort_values("date")
        latest_rows = (
            subset.groupby("food", as_index=False)
            .tail(1)
            .sort_values("food")
            .reset_index(drop=True)
        )

        return (
            resolved_market,
            resolved_price_type,
            latest_rows["date"].max() if not latest_rows.empty else None,
            [
                FoodPriceSnapshot(item=row.food, price=round(float(row.price), 2))
                for row in latest_rows.itertuples(index=False)
            ],
        )

    def calculate_rainfall_correlation(
        self, food_name: str, market: str, price_type: str
    ) -> float:
        resolved_food = resolve_food_name(self._repository, food_name)
        resolved_market = resolve_market_name(self._repository, market)
        resolved_price_type = resolve_price_type(self._repository, price_type)

        price_series = self._filtered_series(
            food_name=resolved_food,
            market=resolved_market,
            price_type=resolved_price_type,
            time_range="all",
        )
        rainfall = self._repository.get_rainfall_dataset()
        if price_series.empty or rainfall.empty:
            raise InsufficientDataError("Not enough data available to calculate correlation.")

        correlations: list[float] = []
        for _, rainfall_group in rainfall.groupby("rainfall_location"):
            merged = price_series.merge(rainfall_group, on="date", how="inner")
            if len(merged) < 2:
                continue
            correlation = merged["price"].corr(merged["rainfall_mm"], method="pearson")
            if correlation is not None and not math.isnan(float(correlation)):
                correlations.append(float(correlation))

        if not correlations:
            raise InsufficientDataError("Not enough overlapping data to calculate correlation.")

        strongest = max(correlations, key=lambda value: abs(value))
        return round(strongest, 4)

    def _filtered_series(
        self,
        food_name: str,
        market: str,
        price_type: str,
        time_range: str,
    ) -> pd.DataFrame:
        dataset = self._repository.get_dataset()
        subset = dataset.loc[
            (dataset["food"] == food_name)
            & (dataset["market"] == market)
            & (dataset["price_type"] == price_type)
        ].sort_values("date")
        return filter_by_time_range(subset, time_range)
