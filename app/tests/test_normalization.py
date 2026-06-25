from __future__ import annotations

import pandas as pd

from app.transformers.dataset_normalizer import DatasetNormalizer


def test_dataset_normalizer_converts_wide_dataset_to_long_format() -> None:
    raw_frame = pd.DataFrame(
        {
            "date": ["2026-06-22", "2026-06-23"],
            "retail_pettah_Tomato": [250, 255],
            "retail_pettah_Beans": [380, 390],
            "wholesale_nuwara_eliya_Green_Chilli": [420, 430],
            "rainfall_nuwara_eliya_mm": [12.5, 18.0],
            "rainfall_polonnaruwa_mm": [3.0, 5.5],
        }
    )

    normalized = DatasetNormalizer().normalize(raw_frame)

    assert list(normalized.prices.columns) == [
        "date",
        "food",
        "market",
        "price_type",
        "price",
    ]
    assert len(normalized.prices) == 6
    assert set(normalized.prices["food"]) == {"Tomato", "Beans", "Green Chilli"}
    assert set(normalized.prices["market"]) == {"Pettah", "Nuwara Eliya"}
    assert set(normalized.prices["price_type"]) == {"retail", "wholesale"}

    assert list(normalized.rainfall.columns) == [
        "date",
        "rainfall_location",
        "rainfall_mm",
    ]
    assert len(normalized.rainfall) == 4
    assert set(normalized.rainfall["rainfall_location"]) == {
        "Nuwara Eliya",
        "Polonnaruwa",
    }
