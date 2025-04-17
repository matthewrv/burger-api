from pydantic import BaseModel
from sqlmodel import select

from app.db import SessionDep
from db.ingredient import Ingredient

from ..router import api_router
from .models import IngredientItem

__all__ = ("IngredientsListResponse", "get_ingredients")


class IngredientsListResponse(BaseModel):
    success: bool
    data: list[IngredientItem]


@api_router.get("/ingredients", response_model=IngredientsListResponse)
async def get_ingredients(db: SessionDep):
    ingredients = db.exec(select(Ingredient)).all()
    return {"success": True, "data": ingredients}
