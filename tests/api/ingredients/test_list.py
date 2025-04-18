from uuid import UUID

from fastapi.testclient import TestClient
from sqlmodel import Session

from db.ingredient import Ingredient


def test_ingredients_list(session: Session, client: TestClient) -> None:
    test_ingredient = Ingredient(
        id=UUID("cae4fd2b-43d4-4e2d-9181-640c1e165ccd"),
        name="test",
        type="bun",
        proteins=10,
        fat=10,
        carbohydrates=20,
        calories=300,
        price=255,
        image="https://example.com",
        image_mobile="https://m.example.com",
        image_large="https://example.com",
        burger_word="тестовый",
    )
    with session.begin():
        session.add(test_ingredient)

    response = client.get("/api/ingredients")
    assert response.status_code == 200

    ingredient_dict = test_ingredient.model_dump()
    ingredient_dict["_id"] = str(ingredient_dict.pop("id"))
    ingredient_dict.pop("burger_word")
    assert response.json() == {"success": True, "data": [ingredient_dict]}
