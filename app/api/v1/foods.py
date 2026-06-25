from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_food_service
from app.schemas.responses import (
    ErrorResponse,
    FoodMetadataResponse,
    FoodsResponse,
    MarketsResponse,
    PriceTypesResponse,
)
from app.services.food_service import FoodService


router = APIRouter(tags=["Catalog"])


@router.get(
    "/foods",
    response_model=FoodsResponse,
    summary="List foods",
    description="Return all food categories dynamically discovered from the dataset.",
    responses={503: {"model": ErrorResponse}},
)
def list_foods(service: FoodService = Depends(get_food_service)) -> FoodsResponse:
    return FoodsResponse(foods=service.get_foods())


@router.get(
    "/markets",
    response_model=MarketsResponse,
    summary="List markets",
    description="Return all available markets discovered from the dataset.",
    responses={503: {"model": ErrorResponse}},
)
def list_markets(service: FoodService = Depends(get_food_service)) -> MarketsResponse:
    return MarketsResponse(markets=service.get_markets())


@router.get(
    "/price-types",
    response_model=PriceTypesResponse,
    summary="List price types",
    description="Return all price types currently available in the normalized dataset.",
    responses={503: {"model": ErrorResponse}},
)
def list_price_types(
    service: FoodService = Depends(get_food_service),
) -> PriceTypesResponse:
    return PriceTypesResponse(price_types=service.get_price_types())


@router.get(
    "/foods/{food_name}",
    response_model=FoodMetadataResponse,
    summary="Get food metadata",
    description="Return market and price type availability for a single food category.",
    responses={404: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
def get_food_metadata(
    food_name: str,
    service: FoodService = Depends(get_food_service),
) -> FoodMetadataResponse:
    metadata = service.get_food_metadata(food_name)
    return FoodMetadataResponse(
        food=metadata.food,
        available_markets=metadata.available_markets,
        available_price_types=metadata.available_price_types,
    )
