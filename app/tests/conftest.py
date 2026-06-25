from __future__ import annotations

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.api.v1.dependencies import ServiceContainer
from app.domain.interfaces.repository import DatasetRepository
from app.main import create_app
from app.services.analytics_service import AnalyticsService
from app.services.food_service import FoodService
from app.services.forecast_service import ForecastService
from app.services.trend_service import TrendService
from app.forecasting.linear_regression import LinearRegressionForecastProvider
from app.forecasting.moving_average import MovingAverageForecastProvider


class InMemoryRepository(DatasetRepository):
    def __init__(self, dataset: pd.DataFrame, rainfall: pd.DataFrame) -> None:
        self._dataset = dataset
        self._rainfall = rainfall

    def get_dataset(self) -> pd.DataFrame:
        return self._dataset.copy()

    def get_rainfall_dataset(self) -> pd.DataFrame:
        return self._rainfall.copy()

    def get_foods(self) -> list[str]:
        return sorted(self._dataset["food"].unique().tolist())

    def get_markets(self) -> list[str]:
        return sorted(self._dataset["market"].unique().tolist())

    def get_price_types(self) -> list[str]:
        return sorted(self._dataset["price_type"].unique().tolist())

    def get_rainfall_locations(self) -> list[str]:
        return sorted(self._rainfall["rainfall_location"].unique().tolist())


@pytest.fixture()
def sample_price_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04", "2026-01-05"]
                * 3
            ),
            "food": [
                "Tomato",
                "Tomato",
                "Tomato",
                "Tomato",
                "Tomato",
            ]
            + [
                "Beans",
                "Beans",
                "Beans",
                "Beans",
                "Beans",
            ]
            + [
                "Tomato",
                "Tomato",
                "Tomato",
                "Tomato",
                "Tomato",
            ],
            "market": [
                "Pettah",
                "Pettah",
                "Pettah",
                "Pettah",
                "Pettah",
            ]
            + [
                "Pettah",
                "Pettah",
                "Pettah",
                "Pettah",
                "Pettah",
            ]
            + [
                "Dambulla",
                "Dambulla",
                "Dambulla",
                "Dambulla",
                "Dambulla",
            ],
            "price_type": ["retail"] * 15,
            "price": [
                100.0,
                110.0,
                120.0,
                130.0,
                140.0,
                200.0,
                210.0,
                220.0,
                230.0,
                240.0,
                90.0,
                95.0,
                100.0,
                105.0,
                110.0,
            ],
        }
    )


@pytest.fixture()
def sample_rainfall_dataset() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2026-01-01",
                    "2026-01-02",
                    "2026-01-03",
                    "2026-01-04",
                    "2026-01-05",
                    "2026-01-01",
                    "2026-01-02",
                    "2026-01-03",
                    "2026-01-04",
                    "2026-01-05",
                ]
            ),
            "rainfall_location": ["Nuwara Eliya"] * 5 + ["Polonnaruwa"] * 5,
            "rainfall_mm": [10.0, 20.0, 30.0, 40.0, 50.0, 50.0, 40.0, 30.0, 20.0, 10.0],
        }
    )


@pytest.fixture()
def in_memory_repository(
    sample_price_dataset: pd.DataFrame,
    sample_rainfall_dataset: pd.DataFrame,
) -> InMemoryRepository:
    return InMemoryRepository(sample_price_dataset, sample_rainfall_dataset)


@pytest.fixture()
def client(in_memory_repository: InMemoryRepository) -> TestClient:
    providers = {
        "moving_average": MovingAverageForecastProvider(window_size=3),
        "linear_regression": LinearRegressionForecastProvider(),
    }
    container = ServiceContainer(
        repository=in_memory_repository,
        food_service=FoodService(in_memory_repository),
        trend_service=TrendService(in_memory_repository),
        analytics_service=AnalyticsService(in_memory_repository),
        forecast_service=ForecastService(in_memory_repository, providers),
    )
    app = create_app(container=container)
    return TestClient(app)
