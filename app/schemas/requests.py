from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TimeRange(str, Enum):
    DAYS_7 = "7d"
    DAYS_30 = "30d"
    MONTHS_3 = "3m"
    MONTHS_6 = "6m"
    YEAR_1 = "1y"
    YEARS_2 = "2y"
    ALL = "all"


class TrendQueryParams(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "market": "pettah",
                "price_type": "retail",
                "time_range": "30d",
            }
        },
    )

    market: str = Field(examples=["pettah"])
    price_type: str = Field(examples=["retail"])
    time_range: TimeRange = Field(default=TimeRange.DAYS_30)


class StatisticsQueryParams(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "market": "pettah",
                "price_type": "retail",
                "time_range": "30d",
            }
        },
    )

    market: str = Field(examples=["pettah"])
    price_type: str = Field(examples=["retail"])
    time_range: TimeRange = Field(default=TimeRange.DAYS_30)


class ForecastQueryParams(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "market": "pettah",
                "price_type": "retail",
                "days_ahead": 7,
                "model": "moving_average",
            }
        },
    )

    market: str = Field(examples=["pettah"])
    price_type: str = Field(examples=["retail"])
    days_ahead: int = Field(default=7, ge=1, le=90)
    model: str = Field(default="moving_average", examples=["moving_average"])


class CompareMarketsQueryParams(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"example": {"food": "Tomato", "price_type": "retail"}},
    )

    food: str = Field(examples=["Tomato"])
    price_type: str = Field(examples=["retail"])


class CompareFoodsQueryParams(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"example": {"market": "pettah", "price_type": "retail"}},
    )

    market: str = Field(examples=["pettah"])
    price_type: str = Field(examples=["retail"])


class RainfallCorrelationQueryParams(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "food": "Tomato",
                "market": "pettah",
                "price_type": "retail",
            }
        },
    )

    food: str = Field(examples=["Tomato"])
    market: str = Field(examples=["pettah"])
    price_type: str = Field(examples=["retail"])
