from __future__ import annotations

import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.api.v1 import analytics, foods, forecast, health, trends
from app.api.v1.dependencies import ServiceContainer, build_service_container
from app.core.config import Settings, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    settings: Settings = application.state.settings
    configure_logging(settings.debug)
    logger.info(
        "application_starting",
        extra={"app_name": settings.app_name, "api_version": settings.api_version},
    )
    yield
    logger.info("application_stopping")


def create_app(
    settings: Settings | None = None,
    container: ServiceContainer | None = None,
) -> FastAPI:
    app_settings = settings or get_settings()
    service_container = container or build_service_container(app_settings)

    application = FastAPI(
        title=app_settings.app_name,
        version=app_settings.api_version,
        description=(
            "Production-oriented backend for Sri Lankan food price analytics, "
            "forecasting, and environmental impact exploration."
        ),
        debug=app_settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    application.state.settings = app_settings
    application.state.container = service_container

    register_exception_handlers(application)

    @application.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "request_completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response

    @application.get(
        "/debug",
        summary="Debug dataset configuration",
        description="Return the configured Hugging Face dataset identifier and file name.",
    )
    def debug() -> dict[str, str]:
        return {
            "dataset_id": application.state.settings.hf_dataset_id,
            "dataset_file": application.state.settings.hf_dataset_file,
        }

    api_prefix = f"/api/{app_settings.api_version}"
    application.include_router(health.router, prefix=api_prefix)
    application.include_router(foods.router, prefix=api_prefix)
    application.include_router(trends.router, prefix=api_prefix)
    application.include_router(analytics.router, prefix=api_prefix)
    application.include_router(forecast.router, prefix=api_prefix)
    return application



app = create_app()
