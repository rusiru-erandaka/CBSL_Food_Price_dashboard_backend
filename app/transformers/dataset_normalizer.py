from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import pandas as pd

from app.core.text import humanize_label


@dataclass(frozen=True, slots=True)
class NormalizedDataset:
    prices: pd.DataFrame
    rainfall: pd.DataFrame


class DatasetNormalizer:
    """Transform the source wide dataset into long-format analytical tables."""

    DATE_COLUMN = "date"
    RAINFALL_PREFIX = "rainfall_"
    RAINFALL_SUFFIX = "_mm"

    def normalize(self, dataframe: pd.DataFrame) -> NormalizedDataset:
        working_frame = dataframe.copy()
        if self.DATE_COLUMN not in working_frame.columns:
            raise ValueError("Dataset must include a 'date' column.")

        working_frame[self.DATE_COLUMN] = pd.to_datetime(
            working_frame[self.DATE_COLUMN],
            errors="coerce",
        )
        working_frame = working_frame.dropna(subset=[self.DATE_COLUMN]).sort_values(
            by=self.DATE_COLUMN
        )

        prices = self._normalize_prices(working_frame)
        rainfall = self._normalize_rainfall(working_frame)
        return NormalizedDataset(prices=prices, rainfall=rainfall)

    def _normalize_prices(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        price_columns = [
            column
            for column in dataframe.columns
            if column != self.DATE_COLUMN and not self._is_rainfall_column(column)
        ]
        parsed_columns = self._parse_price_columns(price_columns)

        if not parsed_columns:
            return pd.DataFrame(
                columns=["date", "food", "market", "price_type", "price"]
            )

        rename_mapping = {
            column: f"{price_type}|||{market}|||{food}"
            for column, price_type, market, food in parsed_columns
        }
        melted = dataframe[[self.DATE_COLUMN, *rename_mapping.keys()]].rename(
            columns=rename_mapping
        )
        normalized = melted.melt(
            id_vars=[self.DATE_COLUMN],
            var_name="series_key",
            value_name="price",
        )

        parts = normalized["series_key"].str.split(r"\|\|\|", expand=True)
        normalized["price_type"] = parts[0]
        normalized["market"] = parts[1]
        normalized["food"] = parts[2]
        normalized["price"] = pd.to_numeric(normalized["price"], errors="coerce")

        normalized = normalized.dropna(subset=["price"]).copy()
        normalized["price"] = normalized["price"].astype(float)

        return (
            normalized.rename(columns={self.DATE_COLUMN: "date"})[
                ["date", "food", "market", "price_type", "price"]
            ]
            .sort_values(by=["date", "food", "market", "price_type"])
            .reset_index(drop=True)
        )

    def _normalize_rainfall(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        rainfall_columns = [
            column for column in dataframe.columns if self._is_rainfall_column(column)
        ]
        if not rainfall_columns:
            return pd.DataFrame(columns=["date", "rainfall_location", "rainfall_mm"])

        rename_mapping = {
            column: humanize_label(
                column.removeprefix(self.RAINFALL_PREFIX).removesuffix(
                    self.RAINFALL_SUFFIX
                )
            )
            for column in rainfall_columns
        }
        melted = dataframe[[self.DATE_COLUMN, *rainfall_columns]].rename(
            columns=rename_mapping
        )
        normalized = melted.melt(
            id_vars=[self.DATE_COLUMN],
            var_name="rainfall_location",
            value_name="rainfall_mm",
        )
        normalized["rainfall_mm"] = pd.to_numeric(
            normalized["rainfall_mm"], errors="coerce"
        )

        return (
            normalized.dropna(subset=["rainfall_mm"])
            .rename(columns={self.DATE_COLUMN: "date"})[
                ["date", "rainfall_location", "rainfall_mm"]
            ]
            .sort_values(by=["date", "rainfall_location"])
            .reset_index(drop=True)
        )

    def _parse_price_columns(
        self, columns: list[str]
    ) -> list[tuple[str, str, str, str]]:
        candidate_splits: dict[str, list[tuple[str, str, str]]] = {}
        market_counter: Counter[str] = Counter()
        food_counter: Counter[str] = Counter()

        for column in columns:
            parts = column.split("_")
            if len(parts) < 3:
                continue

            price_type = parts[0].lower()
            remaining = parts[1:]
            splits: list[tuple[str, str, str]] = []

            for index in range(1, len(remaining)):
                raw_market = "_".join(remaining[:index])
                raw_food = "_".join(remaining[index:])
                market = humanize_label(raw_market)
                food = humanize_label(raw_food)
                splits.append((price_type, market, food))
                market_counter[market] += 1
                food_counter[food] += 1

            candidate_splits[column] = splits

        parsed: list[tuple[str, str, str, str]] = []
        for column, splits in candidate_splits.items():
            if not splits:
                continue

            price_type, market, food = max(
                splits,
                key=lambda item: (
                    market_counter[item[1]] * food_counter[item[2]],
                    market_counter[item[1]] + food_counter[item[2]],
                    -len(item[1]),
                ),
            )
            parsed.append((column, price_type, market, food))

        return parsed

    def _is_rainfall_column(self, column: str) -> bool:
        return column.startswith(self.RAINFALL_PREFIX) and column.endswith(
            self.RAINFALL_SUFFIX
        )
