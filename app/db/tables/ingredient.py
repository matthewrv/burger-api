from pydantic import UUID4
from sqlmodel import Field, SQLModel

from app.db.utils import random_uuid


class Ingredient(SQLModel, table=True):
    id: UUID4 = Field(default_factory=random_uuid, primary_key=True)
    name: str = Field(max_length=255)
    type: str
    proteins: int
    fat: int
    carbohydrates: int
    calories: int
    price: int
    image: str
    image_mobile: str
    image_large: str
    burger_word: str
