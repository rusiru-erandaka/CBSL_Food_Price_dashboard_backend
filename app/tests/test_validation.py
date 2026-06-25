from __future__ import annotations


def test_invalid_time_range_returns_structured_validation_error(client) -> None:
    response = client.get(
        "/api/v1/foods/Tomato/trends",
        params={"market": "Pettah", "price_type": "retail", "time_range": "10d"},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"] == "ValidationError"
    assert "time_range" in payload["message"]


def test_missing_required_query_parameter_returns_structured_validation_error(
    client,
) -> None:
    response = client.get(
        "/api/v1/foods/Tomato/forecast",
        params={"price_type": "retail", "days_ahead": 2},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"] == "ValidationError"
    assert "market" in payload["message"]
