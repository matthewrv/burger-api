import datetime
from uuid import uuid4

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import UUID4, BaseModel, Field
from sqlmodel import col, select

from app.db import SessionDep
from app.security import UserDep
from db.ingredient import Ingredient
from db.order import Order as DbOrder
from db.order_ingredient import OrderIngredient

from ..router import api_router

__all__ = ("OrderCreateRequest", "OrderCreateResponse", "create_order")


class OrderCreateRequest(BaseModel):
    ingredients: list[UUID4] = Field(min_length=1, max_length=20)


class CreatedOrder(BaseModel):
    id: UUID4
    number: int

class OrderCreateResponse(BaseModel):
    order: CreatedOrder


class OrderCreateFailResponse(BaseModel):
    success: bool
    error: str


@api_router.post(
    "/orders",
    response_model=OrderCreateResponse,
    responses={422: {"model": OrderCreateFailResponse}},
)
async def create_order(
    order: OrderCreateRequest, session: SessionDep, user: UserDep
) -> DbOrder:
    with session.begin():
        ingredients = session.exec(
            select(Ingredient).where(col(Ingredient.id).in_(order.ingredients))
        ).all()
        ingredients_map = {ingredient.id: ingredient for ingredient in ingredients}

        if len(ingredients_map) < len(set(order.ingredients)):
            return JSONResponse(
                {"success": False, "error": "unknown ingredients"},
                status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # use dict for deduplicating ingredients
        adjectives = {
            ingredients_map[ingredient].burger_word: ""
            for ingredient in order.ingredients
        }
        name = " ".join(adjectives | {"бургер": ""})
        name = name.capitalize()

        dbOrder = DbOrder(
            name=name,
            number=0,  # FIXME generate serial number
            owner_id=user.id,
            status="pending",
        )
        session.add(dbOrder)

        order_ingredients = [
            OrderIngredient(order_id=dbOrder.id, ingredient_id=ingredient.id)
            for ingredient in ingredients
        ]
        session.add_all(order_ingredients)

    return {'order': dbOrder}
