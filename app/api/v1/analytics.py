from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_analytics_service
from app.schemas.requests import (
    CompareFoodsQueryParams,
    CompareMarketsQueryParams,
    RainfallCorrelationQueryParams,
    StatisticsQueryParams,
)
from app.schemas.responses import (
    CompareFoodsResponse,
    CompareMarketsResponse,
    ErrorResponse,
    FoodStatisticsResponse,
    PriceSnapshotResponse,
    RainfallCorrelationResponse,
)
from app.services.analytics_service import AnalyticsService


router = APIRouter(tags=["Analytics"])


@router.get(
    "/foods/{food_name}/statistics",
    response_model=FoodStatisticsResponse,
    summary="Get food price statistics",
    description="Return descriptive statistics for a filtered food price series.",
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def get_food_statistics(
    food_name: str,
    params: StatisticsQueryParams = Depends(),
    service: AnalyticsService = Depends(get_analytics_service),
) -> FoodStatisticsResponse:
    statistics = service.get_statistics(
        food_name=food_name,
        market=params.market,
        price_type=params.price_type,
        time_range=params.time_range.value,
    )
    return FoodStatisticsResponse(
        food=statistics.food,
        market=statistics.market,
        price_type=statistics.price_type,
        min_price=statistics.min_price,
        max_price=statistics.max_price,
        avg_price=statistics.avg_price,
        current_price=statistics.current_price,
        price_change_percent=statistics.price_change_percent,
        volatility=statistics.volatility,
    )


@router.get(
    "/compare-markets",
    response_model=CompareMarketsResponse,
    summary="Compare latest prices across markets",
    description="Return the latest available price for one food across all markets.",
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def compare_markets(
    params: CompareMarketsQueryParams = Depends(),
    service: AnalyticsService = Depends(get_analytics_service),
) -> CompareMarketsResponse:
    food, price_type, as_of, snapshots = service.compare_markets(
        food_name=params.food,
        price_type=params.price_type,
    )
    return CompareMarketsResponse(
        food=food,
        price_type=price_type,
        as_of=as_of.date() if as_of is not None else None,
        markets=[
            PriceSnapshotResponse(item=snapshot.item, price=snapshot.price)
            for snapshot in snapshots
        ],
    )


@router.get(
    "/compare-foods",
    response_model=CompareFoodsResponse,
    summary="Compare latest prices across foods",
    description="Return the latest available price for all foods in one market.",
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def compare_foods(
    params: CompareFoodsQueryParams = Depends(),
    service: AnalyticsService = Depends(get_analytics_service),
) -> CompareFoodsResponse:
    market, price_type, as_of, snapshots = service.compare_foods(
        market=params.market,
        price_type=params.price_type,
    )
    return CompareFoodsResponse(
        market=market,
        price_type=price_type,
        as_of=as_of.date() if as_of is not None else None,
        foods=[
            PriceSnapshotResponse(item=snapshot.item, price=snapshot.price)
            for snapshot in snapshots
        ],
    )


@router.get(
    "/rainfall-correlation",
    response_model=RainfallCorrelationResponse,
    summary="Calculate rainfall correlation",
    description=(
        "Calculate the Pearson correlation between a filtered price series and the "
        "available rainfall series, returning the strongest overlap-based correlation."
    ),
    responses={
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
)
def get_rainfall_correlation(
    params: RainfallCorrelationQueryParams = Depends(),
    service: AnalyticsService = Depends(get_analytics_service),
) -> RainfallCorrelationResponse:
    correlation = service.calculate_rainfall_correlation(
        food_name=params.food,
        market=params.market,
        price_type=params.price_type,
    )
    return RainfallCorrelationResponse(correlation=correlation)
