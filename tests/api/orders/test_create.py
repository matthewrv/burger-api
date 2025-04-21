import uuid

import pytest
from fastapi.testclient import TestClient
from snapshottest.pytest import PyTestSnapshotTest
from sqlmodel import Session, select

from app import security
from db.ingredient import Ingredient
from db.order import Order
from tests.conftest import SampleUser


@pytest.mark.now("2025-04-21T10:50:49.105731Z")
def test_create_order_happy_path(
    session: Session,
    client: TestClient,
    test_user: SampleUser,
    ingredients: list[Ingredient],
    snapshot: PyTestSnapshotTest,
) -> None:
    bun = next(ingredient for ingredient in ingredients if ingredient.type == "bun")
    ingredients.remove(bun)

    burger_ingredients = [str(ingredient.id) for ingredient in ingredients]
    burger_ingredients = [str(bun.id), *burger_ingredients, str(bun.id)]

    with client.websocket_connect("/api/orders/all") as websocket:
        data = websocket.receive_json()
        snapshot.assert_match(data)

        token = security.create_access_token(test_user)
        response = client.post(
            "/api/orders",
            json={"ingredients": burger_ingredients},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        snapshot.assert_match(response.json())

        data = websocket.receive_json()
        snapshot.assert_match(data)

    with session.begin():
        db_orders = session.exec(select(Order)).all()
        assert len(db_orders) == 1


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
