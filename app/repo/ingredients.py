from typing import Annotated, Sequence

from fastapi import Depends
from pydantic import UUID4
from sqlmodel import col, select

from app.db import Ingredient
from app.db.db import SessionDep
from app.repo.base_repo import BaseRepo, as_transaction

__all__ = ("IngredientsRepo", "IngredientsRepoDep")


class IngredientsRepo(BaseRepo):
    @as_transaction
    async def get_ingredients_by_ids(
        self, ingredient_ids: list[UUID4]
    ) -> list[Ingredient]:
        result = await self._session.exec(
            select(Ingredient).where(col(Ingredient.id).in_(ingredient_ids))
        )
        ingredients = result.all()

        ingredients_map = {ingredient.id: ingredient for ingredient in ingredients}
        return [
            ingredients_map[id_] for id_ in ingredient_ids if id_ in ingredients_map
        ]

    @as_transaction
    async def get_all_active_ingredients(self) -> Sequence[Ingredient]:
        result = await self._session.exec(select(Ingredient))
        return result.all()


async def _get_ingredients_repo(session: SessionDep) -> IngredientsRepo:
    return IngredientsRepo(session)


IngredientsRepoDep = Annotated[IngredientsRepo, Depends(_get_ingredients_repo)]
