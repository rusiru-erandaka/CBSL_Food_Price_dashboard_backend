from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field, ValidationError

BASE_DIR = Path(__file__).resolve().parent.parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(extra="ignore")

    app_name: str = Field(default="Sri Lankan Food Price Analytics Platform")
    api_version: str = Field(default="v1")
    debug: bool = Field(default=False)
    hf_dataset_id: str = Field(default="")
    hf_dataset_file: str = Field(default="")
    request_timeout_seconds: int = Field(default=30, ge=1, le=300)
    dataset_cache_ttl_seconds: int = Field(default=3600, ge=0)

    @classmethod
    def from_environment(cls) -> "Settings":
        data = {
            "app_name": os.getenv("APP_NAME", cls.model_fields["app_name"].default),
            "api_version": os.getenv("API_VERSION", cls.model_fields["api_version"].default),
            "debug": os.getenv("DEBUG", str(cls.model_fields["debug"].default)).lower()
            in {"1", "true", "yes", "on"},
            "hf_dataset_id": os.getenv(
                "HF_DATASET_ID",
                cls.model_fields["hf_dataset_id"].default,
            ),
            "hf_dataset_file": os.getenv(
                "HF_DATASET_FILE",
                cls.model_fields["hf_dataset_file"].default,
            ),
            "request_timeout_seconds": os.getenv(
                "REQUEST_TIMEOUT_SECONDS",
                cls.model_fields["request_timeout_seconds"].default,
            ),
            "dataset_cache_ttl_seconds": os.getenv(
                "DATASET_CACHE_TTL_SECONDS",
                cls.model_fields["dataset_cache_ttl_seconds"].default,
            ),
        }
        try:
            return cls.model_validate(data)
        except ValidationError as exc:
            raise RuntimeError(f"Invalid application settings: {exc}") from exc


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings.from_environment()


settings = get_settings()
