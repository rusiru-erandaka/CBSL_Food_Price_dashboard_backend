from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_trend_service
from app.schemas.requests import TrendQueryParams
from app.schemas.responses import ErrorResponse, FoodTrendResponse, TrendPointResponse
from app.services.trend_service import TrendService


router = APIRouter(tags=["Trends"])


@router.get(
    "/foods/{food_name}/trends",
    response_model=FoodTrendResponse,
    summary="Get food price trend",
    description="Return a historical time series for one food, market, and price type.",
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def get_food_trends(
    food_name: str,
    params: TrendQueryParams = Depends(),
    service: TrendService = Depends(get_trend_service),
) -> FoodTrendResponse:
    trend = service.get_trend(
        food_name=food_name,
        market=params.market,
        price_type=params.price_type,
        time_range=params.time_range.value,
    )
    return FoodTrendResponse(
        food=trend.food,
        market=trend.market,
        price_type=trend.price_type,
        points=[TrendPointResponse(date=point.date, price=point.price) for point in trend.points],
    )
