from pydantic import UUID4
from sqlmodel import Field, SQLModel

from db.utils import random_uuid


class OrderIngredient(SQLModel, table=True):
    id: UUID4 = Field(default_factory=random_uuid, primary_key=True)
    order_id: UUID4 = Field(foreign_key="order.id")
    ingredient_id: UUID4 = Field(foreign_key="ingredient.id")
