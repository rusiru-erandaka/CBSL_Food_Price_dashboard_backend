from __future__ import annotations


def test_get_food_trend_points(client) -> None:
    response = client.get(
        "/api/v1/foods/Tomato/trends",
        params={"market": "pettah", "price_type": "retail", "time_range": "all"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["food"] == "Tomato"
    assert payload["market"] == "Pettah"
    assert payload["price_type"] == "retail"
    assert payload["points"][0] == {"date": "2026-01-01", "price": 100.0}
    assert payload["points"][-1] == {"date": "2026-01-05", "price": 140.0}
