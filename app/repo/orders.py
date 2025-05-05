import datetime
import typing
from typing import Annotated

from fastapi import Depends
from pydantic import UUID4, BaseModel, Field
from sqlmodel import col, desc, func, select

from app.db import Ingredient, OrderIngredient, SessionDep, User
from app.db import Order as DbOrder
from app.db.utils import utc_now
from app.repo.ingredients import IngredientsRepoDep

from .base_repo import BaseRepo, as_transaction
from .common import Error

__all__ = ("OrderShallow", "OrderFull", "OrdersRepo")


class OrderShallow(BaseModel):
    id: UUID4
    created_at: datetime.datetime
    updated_at: datetime.datetime
    name: str
    number: int
    owner_id: UUID4
    status: str


class OrderFull(OrderShallow):
    ingredients: list[UUID4] = Field(default_factory=list)


class OrdersRepo(BaseRepo):
    def __init__(
        self, session: SessionDep, ingredients_repo: IngredientsRepoDep
    ) -> None:
        super().__init__(session)
        self._ingredients_repo = ingredients_repo

    @as_transaction
    async def get_recent_orders_full(
        self, limit: int = 50, user: User | None = None
    ) -> list[OrderFull]:
        query = select(DbOrder).order_by(desc(DbOrder.created_at)).limit(limit)
        if user:
            query = (
                select(DbOrder)
                .where(col(DbOrder.owner_id) == user.id)
                .order_by(desc(DbOrder.created_at))
                .limit(limit)
            )
        orders_result = await self._session.exec(query)
        orders = orders_result.all()

        order_ids = [order.id for order in orders]
        ingredients_result = await self._session.exec(
            select(OrderIngredient).where(col(OrderIngredient.order_id).in_(order_ids))
        )
        ingredients = ingredients_result.all()

        orders_map = {
            order.id: OrderFull.model_validate(order, from_attributes=True)
            for order in orders
        }
        for ingredient in ingredients:
            orders_map[ingredient.order_id].ingredients.append(ingredient.ingredient_id)

        return list(orders_map.values())

    @as_transaction
    async def get_orders_count(self) -> tuple[int, int]:
        total_orders_query = select(func.count()).select_from(DbOrder)
        total_orders_result = await self._session.exec(total_orders_query)
        total_orders = total_orders_result.one()

        now = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_orders_query = (
            select(func.count())
            .select_from(DbOrder)
            .where(col(DbOrder.created_at) >= now)
        )
        today_orders_result = await self._session.exec(today_orders_query)
        today_orders = today_orders_result.one()

        return (total_orders, today_orders)

    @as_transaction
    async def create_order(
        self, ingredient_ids: list[UUID4], user: User
    ) -> Error | OrderFull:
        ingredients = await self._ingredients_repo.get_ingredients_by_ids(
            ingredient_ids
        )

        if len(ingredients) < len(ingredient_ids):
            return Error(message="unknown ingredients")

        # postgresql identity column requires None
        assert self._session.bind is not None
        dialect_name = self._session.bind.dialect.name
        number = None if dialect_name == "postgresql" else 0

        dbOrder = DbOrder(
            name=self._burger_name_from_ingredients(ingredients),
            number=number,  # type: ignore[arg-type]
            owner_id=user.id,
            status="pending",
        )
        self._session.add(dbOrder)

        order_ingredients = [
            OrderIngredient(order_id=dbOrder.id, ingredient_id=ingredient)
            for ingredient in ingredient_ids
        ]
        self._session.add_all(order_ingredients)
        saved_order = typing.cast(
            DbOrder, await self.get_shallow_order_by_id(dbOrder.id)
        )

        return self._compose_order_full(saved_order, order_ingredients)

    @as_transaction
    async def get_shallow_order_by_id(self, id_: UUID4) -> DbOrder | None:
        result = await self._session.exec(select(DbOrder).where(col(DbOrder.id) == id_))
        return result.one_or_none()

    @staticmethod
    def _burger_name_from_ingredients(ingredients: list[Ingredient]) -> str:
        # use dict for deduplicating ingredients and preserving order
        adjectives = {ingredient.burger_word: "" for ingredient in ingredients}
        name = " ".join(adjectives | {"бургер": ""})
        name = name.capitalize()
        return name

    @staticmethod
    def _compose_order_full(
        dbOrder: DbOrder, ingredients: list[OrderIngredient]
    ) -> OrderFull:
        return OrderFull(
            id=dbOrder.id,
            created_at=dbOrder.created_at,
            updated_at=dbOrder.updated_at,
            name=dbOrder.name,
            number=dbOrder.number,
            owner_id=dbOrder.owner_id,
            status=dbOrder.status,
            ingredients=[ingredient.ingredient_id for ingredient in ingredients],
        )


async def _get_orders_repo(
    session: SessionDep, ingredients_repo: IngredientsRepoDep
) -> OrdersRepo:
    return OrdersRepo(session, ingredients_repo)


OrdersRepoDep = Annotated[OrdersRepo, Depends(_get_orders_repo)]
