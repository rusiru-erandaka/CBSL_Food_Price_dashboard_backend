from __future__ import annotations

from datetime import timedelta

import pandas as pd

from app.domain.entities.forecast import ForecastPoint
from app.forecasting.base import BaseForecastProvider


class MovingAverageForecastProvider(BaseForecastProvider):
    name = "moving_average"

    def __init__(self, window_size: int = 7) -> None:
        self.window_size = window_size

    def forecast(self, series: pd.DataFrame, days_ahead: int) -> list[ForecastPoint]:
        prepared = self._prepare_series(series)
        moving_average = float(
            prepared["price"].tail(self.window_size).mean()
            if len(prepared) >= self.window_size
            else prepared["price"].mean()
        )
        last_date = prepared["date"].iloc[-1].date()

        return [
            ForecastPoint(
                date=last_date + timedelta(days=offset),
                predicted_price=round(moving_average, 2),
            )
            for offset in range(1, days_ahead + 1)
        ]
