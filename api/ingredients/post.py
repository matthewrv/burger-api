from pydantic import UUID4, BaseModel, Field
from sqlmodel import insert, select
from app.di import SessionDep
from db.ingredient import Ingredient
from app.app import app
from .models import IngredientItem


class AddIngredientResponse(BaseModel):
    id: str


@app.put("/api/ingredients", response_model=AddIngredientResponse)
async def add_ingredient(ingredient: IngredientItem, db: SessionDep) -> IngredientItem:
    test_dict = ingredient.model_dump()
    print(test_dict)
    with db.begin():
        db.exec(insert(Ingredient).values([ingredient.model_dump()]))
    return ingredient
