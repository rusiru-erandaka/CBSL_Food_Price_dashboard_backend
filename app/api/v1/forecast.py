from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_forecast_service
from app.schemas.requests import ForecastQueryParams
from app.schemas.responses import (
    ErrorResponse,
    FoodForecastResponse,
    ForecastPointResponse,
)
from app.services.forecast_service import ForecastService


router = APIRouter(tags=["Forecasting"])


@router.get(
    "/foods/{food_name}/forecast",
    response_model=FoodForecastResponse,
    summary="Forecast food prices",
    description="Generate a forward-looking forecast using the selected model provider.",
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def get_food_forecast(
    food_name: str,
    params: ForecastQueryParams = Depends(),
    service: ForecastService = Depends(get_forecast_service),
) -> FoodForecastResponse:
    forecast = service.get_forecast(
        food_name=food_name,
        market=params.market,
        price_type=params.price_type,
        days_ahead=params.days_ahead,
        model=params.model,
    )
    return FoodForecastResponse(
        food=forecast.food,
        market=forecast.market,
        price_type=forecast.price_type,
        model=forecast.model,
        forecast=[
            ForecastPointResponse(
                date=point.date,
                predicted_price=point.predicted_price,
            )
            for point in forecast.forecast
        ],
    )
