import uuid
from unittest import mock

from fastapi.testclient import TestClient
from pytest import MonkeyPatch
from sqlmodel import Session, select

from app import security
from db.ingredient import Ingredient
from db.order import Order
from tests.conftest import SampleUser


def test_create_order(
    session: Session,
    client: TestClient,
    test_user: SampleUser,
    ingredients: list[Ingredient],
) -> None:
    bun = next(ingredient for ingredient in ingredients if ingredient.type == "bun")
    ingredients.remove(bun)

    burger_ingredients = [str(ingredient.id) for ingredient in ingredients]
    burger_ingredients = [str(bun.id), *burger_ingredients, str(bun.id)]

    token = security.create_access_token(test_user)
    response = client.post(
        "/api/orders",
        json={"ingredients": burger_ingredients},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200

    with session.begin():
        db_orders = session.exec(select(Order)).all()
        assert len(db_orders) == 1
        order = db_orders[0]

    response_body = response.json()
    assert response_body == {"order": {"id": str(order.id), "number": 0}}


def test_create_order_fail(
    session: Session,
    client: TestClient,
    test_user: SampleUser,
) -> None:
    token = security.create_access_token(test_user)
    response = client.post(
        "/api/orders",
        json={"ingredients": [str(uuid.uuid4())]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 422

    with session.begin():
        db_orders = session.exec(select(Order)).all()
        assert len(db_orders) == 0

    response_body = response.json()
    assert response_body == {"error": "unknown ingredients", "success": False}
