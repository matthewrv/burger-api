import uuid

from pydantic import UUID4
from sqlmodel import Field, SQLModel


class OrderIngredient(SQLModel, table=True):
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)
    order_id: UUID4 = Field(foreign_key="order.id")
    ingredient_id: UUID4 = Field(foreign_key="ingredient.id")
