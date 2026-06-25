from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
from huggingface_hub import hf_hub_download

from app.core.config import Settings
from app.core.exceptions import DatasetLoadError
from app.core.logging import get_logger
from app.domain.interfaces.repository import DatasetRepository
from app.transformers.dataset_normalizer import DatasetNormalizer


logger = get_logger(__name__)


class HuggingFaceRepository(DatasetRepository):
    """Repository that loads the CSV dataset from a Hugging Face dataset repository."""

    def __init__(self, settings: Settings, normalizer: DatasetNormalizer) -> None:
        self._settings = settings
        self._normalizer = normalizer
        self._dataset_cache: pd.DataFrame | None = None
        self._rainfall_cache: pd.DataFrame | None = None
        self._loaded_at: datetime | None = None

    def get_dataset(self) -> pd.DataFrame:
        self._ensure_loaded()
        assert self._dataset_cache is not None
        return self._dataset_cache.copy()

    def get_rainfall_dataset(self) -> pd.DataFrame:
        self._ensure_loaded()
        assert self._rainfall_cache is not None
        return self._rainfall_cache.copy()

    def get_foods(self) -> list[str]:
        dataset = self.get_dataset()
        return sorted(dataset["food"].dropna().unique().tolist())

    def get_markets(self) -> list[str]:
        dataset = self.get_dataset()
        return sorted(dataset["market"].dropna().unique().tolist())

    def get_price_types(self) -> list[str]:
        dataset = self.get_dataset()
        return sorted(dataset["price_type"].dropna().unique().tolist())

    def get_rainfall_locations(self) -> list[str]:
        rainfall = self.get_rainfall_dataset()
        return sorted(rainfall["rainfall_location"].dropna().unique().tolist())

    def _ensure_loaded(self) -> None:
        if self._dataset_cache is not None and not self._is_cache_expired():
            return
        self._load_from_source()

    def _is_cache_expired(self) -> bool:
        if self._loaded_at is None:
            return True
        ttl = self._settings.dataset_cache_ttl_seconds
        if ttl == 0:
            return True
        return datetime.now(timezone.utc) >= self._loaded_at + timedelta(seconds=ttl)

    def _load_from_source(self) -> None:
        if not self._settings.hf_dataset_id or not self._settings.hf_dataset_file:
            raise DatasetLoadError(
                "HF_DATASET_ID and HF_DATASET_FILE must both be configured."
            )

        logger.info(
            "loading_dataset",
            extra={
                "dataset_id": self._settings.hf_dataset_id,
                "dataset_file": self._settings.hf_dataset_file,
            },
        )

        try:
            dataset_path = hf_hub_download(
                repo_id=self._settings.hf_dataset_id,
                filename=self._settings.hf_dataset_file,
                repo_type="dataset",
                etag_timeout=float(self._settings.request_timeout_seconds),
            )
            raw_frame = pd.read_csv(dataset_path)
        except Exception as exc:
            logger.exception("dataset_download_failed")
            raise DatasetLoadError(f"Failed to download dataset: {exc}") from exc

        try:
            normalized = self._normalizer.normalize(raw_frame)
        except Exception as exc:
            logger.exception("dataset_normalization_failed")
            raise DatasetLoadError(f"Failed to parse dataset: {exc}") from exc

        self._dataset_cache = normalized.prices
        self._rainfall_cache = normalized.rainfall
        self._loaded_at = datetime.now(timezone.utc)

        logger.info(
            "dataset_loaded",
            extra={
                "price_rows": len(self._dataset_cache),
                "rainfall_rows": len(self._rainfall_cache),
            },
        )
