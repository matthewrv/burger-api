from pydantic import BaseModel
from sqlmodel import insert

from app.di import SessionDep
from db.ingredient import Ingredient

from ..router import api_router
from .models import IngredientItem


class AddIngredientResponse(BaseModel):
    id: str


@api_router.put("/ingredients", response_model=AddIngredientResponse)
async def add_ingredient(ingredient: IngredientItem, db: SessionDep) -> IngredientItem:
    test_dict = ingredient.model_dump()
    print(test_dict)
    with db.begin():
        db.exec(insert(Ingredient).values([ingredient.model_dump()]))
    return ingredient
