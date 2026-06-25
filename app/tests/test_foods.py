from __future__ import annotations


def test_list_foods(client) -> None:
    response = client.get("/api/v1/foods")

    assert response.status_code == 200
    assert response.json() == {"foods": ["Beans", "Tomato"]}


def test_get_food_metadata(client) -> None:
    response = client.get("/api/v1/foods/tomato")

    assert response.status_code == 200
    assert response.json() == {
        "food": "Tomato",
        "available_markets": ["Dambulla", "Pettah"],
        "available_price_types": ["retail"],
    }


def test_get_unknown_food_returns_structured_error(client) -> None:
    response = client.get("/api/v1/foods/Cabbage")

    assert response.status_code == 404
    assert response.json() == {
        "error": "FoodNotFoundError",
        "message": "Cabbage not found",
    }
