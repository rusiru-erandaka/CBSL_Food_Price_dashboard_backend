from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from app.domain.entities.forecast import ForecastPoint
from app.forecasting.base import BaseForecastProvider


class LinearRegressionForecastProvider(BaseForecastProvider):
    name = "linear_regression"

    def forecast(self, series: pd.DataFrame, days_ahead: int) -> list[ForecastPoint]:
        prepared = self._prepare_series(series)
        origin = prepared["date"].min()
        day_offsets = (prepared["date"] - origin).dt.days.to_numpy(dtype=float)
        prices = prepared["price"].to_numpy(dtype=float)

        if len(np.unique(day_offsets)) == 1:
            last_price = round(float(prices[-1]), 2)
            last_date = prepared["date"].iloc[-1].date()
            return [
                ForecastPoint(
                    date=last_date + timedelta(days=offset),
                    predicted_price=last_price,
                )
                for offset in range(1, days_ahead + 1)
            ]

        model = LinearRegression()
        model.fit(day_offsets.reshape(-1, 1), prices)

        last_observed_date = prepared["date"].iloc[-1]
        future_offsets = np.arange(
            (last_observed_date - origin).days + 1,
            (last_observed_date - origin).days + days_ahead + 1,
            dtype=float,
        )
        predictions = model.predict(future_offsets.reshape(-1, 1))

        return [
            ForecastPoint(
                date=(last_observed_date + timedelta(days=index + 1)).date(),
                predicted_price=round(max(0.0, float(prediction)), 2),
            )
            for index, prediction in enumerate(predictions)
        ]
