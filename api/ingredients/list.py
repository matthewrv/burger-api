from pydantic import BaseModel
from sqlmodel import select

from app.app import app
from app.di import SessionDep
from db.ingredient import Ingredient

from .models import IngredientItem


class IngredientsListResponse(BaseModel):
    success: bool
    data: list[IngredientItem]


@app.get("/api/ingredients", response_model=IngredientsListResponse)
async def get_ingredients(db: SessionDep):
    ingredients = db.exec(select(Ingredient)).all()
    return {"success": True, "data": ingredients}
