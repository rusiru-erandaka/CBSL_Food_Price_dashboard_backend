from __future__ import annotations


def test_moving_average_forecast(client) -> None:
    response = client.get(
        "/api/v1/foods/Tomato/forecast",
        params={
            "market": "Pettah",
            "price_type": "retail",
            "days_ahead": 3,
            "model": "moving_average",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "food": "Tomato",
        "market": "Pettah",
        "price_type": "retail",
        "model": "moving_average",
        "forecast": [
            {"date": "2026-01-06", "predicted_price": 130.0},
            {"date": "2026-01-07", "predicted_price": 130.0},
            {"date": "2026-01-08", "predicted_price": 130.0},
        ],
    }


def test_linear_regression_forecast(client) -> None:
    response = client.get(
        "/api/v1/foods/Tomato/forecast",
        params={
            "market": "Pettah",
            "price_type": "retail",
            "days_ahead": 2,
            "model": "linear_regression",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["model"] == "linear_regression"
    assert payload["forecast"][0]["date"] == "2026-01-06"
    assert payload["forecast"][0]["predicted_price"] == 150.0
    assert payload["forecast"][1]["predicted_price"] == 160.0
