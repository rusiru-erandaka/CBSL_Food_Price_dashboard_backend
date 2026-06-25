from __future__ import annotations

from dataclasses import dataclass

from fastapi import Request

from app.domain.interfaces.repository import DatasetRepository
from app.forecasting.linear_regression import LinearRegressionForecastProvider
from app.forecasting.moving_average import MovingAverageForecastProvider
from app.repositories.huggingface_repository import HuggingFaceRepository
from app.services.analytics_service import AnalyticsService
from app.services.food_service import FoodService
from app.services.forecast_service import ForecastService
from app.services.trend_service import TrendService
from app.transformers.dataset_normalizer import DatasetNormalizer
from app.core.config import Settings


@dataclass(slots=True)
class ServiceContainer:
    repository: DatasetRepository
    food_service: FoodService
    trend_service: TrendService
    analytics_service: AnalyticsService
    forecast_service: ForecastService


def build_service_container(settings: Settings) -> ServiceContainer:
    repository = HuggingFaceRepository(
        settings=settings,
        normalizer=DatasetNormalizer(),
    )
    providers = {
        "moving_average": MovingAverageForecastProvider(),
        "linear_regression": LinearRegressionForecastProvider(),
    }
    return ServiceContainer(
        repository=repository,
        food_service=FoodService(repository),
        trend_service=TrendService(repository),
        analytics_service=AnalyticsService(repository),
        forecast_service=ForecastService(repository, providers),
    )


def get_container(request: Request) -> ServiceContainer:
    return request.app.state.container


def get_food_service(request: Request) -> FoodService:
    return get_container(request).food_service


def get_trend_service(request: Request) -> TrendService:
    return get_container(request).trend_service


def get_analytics_service(request: Request) -> AnalyticsService:
    return get_container(request).analytics_service


def get_forecast_service(request: Request) -> ForecastService:
    return get_container(request).forecast_service
