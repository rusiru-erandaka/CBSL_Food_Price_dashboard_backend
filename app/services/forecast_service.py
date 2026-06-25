from __future__ import annotations

from app.core.exceptions import ForecastModelNotFoundError
from app.core.logging import get_logger
from app.domain.entities.forecast import FoodForecast
from app.domain.interfaces.forecast_provider import ForecastProvider
from app.domain.interfaces.repository import DatasetRepository
from app.services._utils import (
    resolve_food_name,
    resolve_market_name,
    resolve_price_type,
)


logger = get_logger(__name__)


class ForecastService:
    def __init__(
        self,
        repository: DatasetRepository,
        providers: dict[str, ForecastProvider],
    ) -> None:
        self._repository = repository
        self._providers = providers

    def get_forecast(
        self,
        food_name: str,
        market: str,
        price_type: str,
        days_ahead: int,
        model: str,
    ) -> FoodForecast:
        resolved_food = resolve_food_name(self._repository, food_name)
        resolved_market = resolve_market_name(self._repository, market)
        resolved_price_type = resolve_price_type(self._repository, price_type)
        provider = self._providers.get(model.lower())

        if provider is None:
            raise ForecastModelNotFoundError(f"{model} not found")

        dataset = self._repository.get_dataset()
        subset = dataset.loc[
            (dataset["food"] == resolved_food)
            & (dataset["market"] == resolved_market)
            & (dataset["price_type"] == resolved_price_type)
        ].sort_values("date")

        logger.info(
            "forecast_execution_started",
            extra={
                "food": resolved_food,
                "market": resolved_market,
                "price_type": resolved_price_type,
                "model": provider.name,
                "days_ahead": days_ahead,
            },
        )

        points = provider.forecast(subset, days_ahead)
        return FoodForecast(
            food=resolved_food,
            market=resolved_market,
            price_type=resolved_price_type,
            model=provider.name,
            forecast=points,
        )
