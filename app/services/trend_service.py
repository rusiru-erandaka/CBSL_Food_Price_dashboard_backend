from __future__ import annotations

from app.domain.entities.trend import FoodTrend, TrendPoint
from app.domain.interfaces.repository import DatasetRepository
from app.services._utils import (
    filter_by_time_range,
    resolve_food_name,
    resolve_market_name,
    resolve_price_type,
)


class TrendService:
    def __init__(self, repository: DatasetRepository) -> None:
        self._repository = repository

    def get_trend(
        self,
        food_name: str,
        market: str,
        price_type: str,
        time_range: str,
    ) -> FoodTrend:
        resolved_food = resolve_food_name(self._repository, food_name)
        resolved_market = resolve_market_name(self._repository, market)
        resolved_price_type = resolve_price_type(self._repository, price_type)

        dataset = self._repository.get_dataset()
        subset = dataset.loc[
            (dataset["food"] == resolved_food)
            & (dataset["market"] == resolved_market)
            & (dataset["price_type"] == resolved_price_type)
        ].sort_values("date")
        subset = filter_by_time_range(subset, time_range)

        points = [
            TrendPoint(date=row.date.date(), price=round(float(row.price), 2))
            for row in subset.itertuples(index=False)
        ]
        return FoodTrend(
            food=resolved_food,
            market=resolved_market,
            price_type=resolved_price_type,
            points=points,
        )
