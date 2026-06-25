from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from app.domain.entities.forecast import ForecastPoint


class ForecastProvider(ABC):
    """Interface for forecasting providers."""

    name: str

    @abstractmethod
    def forecast(self, series: pd.DataFrame, days_ahead: int) -> list[ForecastPoint]:
        """Generate forecast points from a normalized time series."""
