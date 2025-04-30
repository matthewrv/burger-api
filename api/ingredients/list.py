from typing import Any

from pydantic import BaseModel

from app.repo.ingredients import IngredientsRepoDep

from ..router import api_router
from .models import IngredientItem

__all__ = ("IngredientsListResponse", "get_ingredients")


class IngredientsListResponse(BaseModel):
    success: bool
    data: list[IngredientItem]


@api_router.get("/ingredients", response_model=IngredientsListResponse)
async def get_ingredients(ingredients_repo: IngredientsRepoDep) -> dict[str, Any]:
    ingredients = await ingredients_repo.get_all_active_ingredients()
    return {"success": True, "data": ingredients}
