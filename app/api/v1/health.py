from __future__ import annotations

from fastapi import APIRouter

from app.schemas.responses import HealthResponse


router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Verify that the API process is running and ready to serve requests.",
)
def get_health() -> HealthResponse:
    return HealthResponse(status="healthy")


