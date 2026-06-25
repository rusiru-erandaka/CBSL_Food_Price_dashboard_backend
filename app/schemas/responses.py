from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "FoodNotFoundError",
                "message": "Tomato not found",
            }
        }
    )

    error: str
    message: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"status": "healthy"}})

    status: str = Field(examples=["healthy"])


class FoodsResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"foods": ["Beans", "Tomato"]}})

    foods: list[str]


class MarketsResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"markets": ["Dambulla", "Pettah"]}}
    )

    markets: list[str]


class PriceTypesResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"price_types": ["retail", "wholesale"]}}
    )

    price_types: list[str]


class FoodMetadataResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "food": "Tomato",
                "available_markets": ["Dambulla", "Pettah"],
                "available_price_types": ["retail", "wholesale"],
            }
        }
    )

    food: str
    available_markets: list[str]
    available_price_types: list[str]


class TrendPointResponse(BaseModel):
    date: date
    price: float


class FoodTrendResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "food": "Tomato",
                "market": "Pettah",
                "price_type": "retail",
                "points": [{"date": "2026-01-01", "price": 250.0}],
            }
        }
    )

    food: str
    market: str
    price_type: str
    points: list[TrendPointResponse]


class FoodStatisticsResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "food": "Tomato",
                "market": "Pettah",
                "price_type": "retail",
                "min_price": 100.0,
                "max_price": 500.0,
                "avg_price": 250.0,
                "current_price": 300.0,
                "price_change_percent": 12.5,
                "volatility": 5.2,
            }
        }
    )

    food: str
    market: str
    price_type: str
    min_price: float
    max_price: float
    avg_price: float
    current_price: float
    price_change_percent: float
    volatility: float


class ForecastPointResponse(BaseModel):
    date: date
    predicted_price: float


class FoodForecastResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "food": "Tomato",
                "market": "Pettah",
                "price_type": "retail",
                "model": "moving_average",
                "forecast": [{"date": "2026-07-01", "predicted_price": 420.0}],
            }
        }
    )

    food: str
    market: str
    price_type: str
    model: str
    forecast: list[ForecastPointResponse]


class PriceSnapshotResponse(BaseModel):
    item: str
    price: float


class CompareMarketsResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "food": "Tomato",
                "price_type": "retail",
                "as_of": "2026-01-05",
                "markets": [{"item": "Pettah", "price": 140.0}],
            }
        }
    )

    food: str
    price_type: str
    as_of: date | None
    markets: list[PriceSnapshotResponse]


class CompareFoodsResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "market": "Pettah",
                "price_type": "retail",
                "as_of": "2026-01-05",
                "foods": [{"item": "Tomato", "price": 140.0}],
            }
        }
    )

    market: str
    price_type: str
    as_of: date | None
    foods: list[PriceSnapshotResponse]


class RainfallCorrelationResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"correlation": 0.43}}
    )

    correlation: float
