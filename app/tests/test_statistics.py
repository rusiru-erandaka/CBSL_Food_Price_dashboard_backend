from __future__ import annotations


def test_get_food_statistics(client) -> None:
    response = client.get(
        "/api/v1/foods/Tomato/statistics",
        params={"market": "pettah", "price_type": "retail", "time_range": "all"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "food": "Tomato",
        "market": "Pettah",
        "price_type": "retail",
        "min_price": 100.0,
        "max_price": 140.0,
        "avg_price": 120.0,
        "current_price": 140.0,
        "price_change_percent": 40.0,
        "volatility": 14.14,
    }


def test_compare_markets_returns_latest_snapshot(client) -> None:
    response = client.get(
        "/api/v1/compare-markets",
        params={"food": "Tomato", "price_type": "retail"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "food": "Tomato",
        "price_type": "retail",
        "as_of": "2026-01-05",
        "markets": [
            {"item": "Dambulla", "price": 110.0},
            {"item": "Pettah", "price": 140.0},
        ],
    }


def test_compare_foods_returns_latest_snapshot(client) -> None:
    response = client.get(
        "/api/v1/compare-foods",
        params={"market": "Pettah", "price_type": "retail"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "market": "Pettah",
        "price_type": "retail",
        "as_of": "2026-01-05",
        "foods": [
            {"item": "Beans", "price": 240.0},
            {"item": "Tomato", "price": 140.0},
        ],
    }


def test_rainfall_correlation_returns_value(client) -> None:
    response = client.get(
        "/api/v1/rainfall-correlation",
        params={"food": "Tomato", "market": "Pettah", "price_type": "retail"},
    )

    assert response.status_code == 200
    assert response.json() == {"correlation": 1.0}
