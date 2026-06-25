from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class DatasetRepository(ABC):
    """Interface for dataset repositories."""

    @abstractmethod
    def get_dataset(self) -> pd.DataFrame:
        """Return normalized price data."""

    @abstractmethod
    def get_rainfall_dataset(self) -> pd.DataFrame:
        """Return normalized rainfall data."""

    @abstractmethod
    def get_foods(self) -> list[str]:
        """Return all discovered foods."""

    @abstractmethod
    def get_markets(self) -> list[str]:
        """Return all discovered markets."""

    @abstractmethod
    def get_price_types(self) -> list[str]:
        """Return all discovered price types."""

    @abstractmethod
    def get_rainfall_locations(self) -> list[str]:
        """Return rainfall source locations."""
