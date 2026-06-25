from __future__ import annotations

from abc import ABC

import pandas as pd

from app.core.exceptions import InsufficientDataError
from app.domain.interfaces.forecast_provider import ForecastProvider


class BaseForecastProvider(ForecastProvider, ABC):
    """Shared validation helpers for forecast providers."""

    def _prepare_series(self, series: pd.DataFrame) -> pd.DataFrame:
        prepared = series[["date", "price"]].copy().sort_values("date").reset_index(
            drop=True
        )
        if prepared.empty:
            raise InsufficientDataError("No data points available for forecasting.")
        return prepared
