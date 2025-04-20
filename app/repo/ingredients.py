from typing import Annotated, Sequence

from fastapi import Depends
from pydantic import UUID4
from sqlmodel import col, select

from app.repo.base_repo import BaseRepo, as_transaction
from db.ingredient import Ingredient

__all__ = ("IngredientsRepo", "IngredientsRepoDep")


class IngredientsRepo(BaseRepo):
    @as_transaction
    def get_ingredients_by_ids(self, ingredient_ids: list[UUID4]) -> list[Ingredient]:
        ingredients = self._session.exec(
            select(Ingredient).where(col(Ingredient.id).in_(ingredient_ids))
        ).all()

        ingredients_map = {ingredient.id: ingredient for ingredient in ingredients}
        return [
            ingredients_map[id_] for id_ in ingredient_ids if id_ in ingredients_map
        ]

    @as_transaction
    def get_all_active_ingredients(self) -> Sequence[Ingredient]:
        return self._session.exec(select(Ingredient)).all()


IngredientsRepoDep = Annotated[IngredientsRepo, Depends(IngredientsRepo)]
