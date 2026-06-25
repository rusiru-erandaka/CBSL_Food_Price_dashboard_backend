from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for application-specific exceptions."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "AppError"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class FoodNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "FoodNotFoundError"


class MarketNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "MarketNotFoundError"


class PriceTypeNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "PriceTypeNotFoundError"


class ForecastModelNotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    error_code = "ForecastModelNotFoundError"


class InvalidTimeRangeError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "InvalidTimeRangeError"


class DatasetLoadError(AppError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "DatasetLoadError"


class InsufficientDataError(AppError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "InsufficientDataError"


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "message": exc.message},
    )


async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "InternalServerError", "message": str(exc)},
    )


async def validation_error_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    messages = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", []))
        messages.append(f"{location}: {error.get('msg', 'Invalid value')}")
    message = "; ".join(messages) if messages else "Request validation failed."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "ValidationError", "message": message},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
