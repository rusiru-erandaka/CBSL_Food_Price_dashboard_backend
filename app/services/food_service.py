from __future__ import annotations

from app.domain.entities.food import FoodMetadata
from app.domain.interfaces.repository import DatasetRepository
from app.services._utils import resolve_food_name


class FoodService:
    def __init__(self, repository: DatasetRepository) -> None:
        self._repository = repository

    def get_foods(self) -> list[str]:
        return self._repository.get_foods()

    def get_markets(self) -> list[str]:
        return self._repository.get_markets()

    def get_price_types(self) -> list[str]:
        return self._repository.get_price_types()

    def get_food_metadata(self, food_name: str) -> FoodMetadata:
        resolved_food = resolve_food_name(self._repository, food_name)
        dataset = self._repository.get_dataset()
        subset = dataset.loc[dataset["food"] == resolved_food]
        return FoodMetadata(
            food=resolved_food,
            available_markets=sorted(subset["market"].dropna().unique().tolist()),
            available_price_types=sorted(
                subset["price_type"].dropna().unique().tolist()
            ),
        )
