from sqlmodel import select

from app.app import app
from app.di import SessionDep
from db.ingredient import Ingredient
from .models import IngredientItem


@app.get("/api/ingredients")
async def get_ingredients(db: SessionDep) -> list[IngredientItem]:
    return db.exec(select(Ingredient)).all()
