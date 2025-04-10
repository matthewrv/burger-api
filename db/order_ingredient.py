from pydantic import UUID4
from sqlmodel import UUID, Field, SQLModel


class OrderIngredient(SQLModel, table=True):
    id: UUID4 = Field(UUID(as_uuid=True), primary_key=True)
    order_id: UUID4 = Field(UUID(as_uuid=True), foreign_key="order.id")
    ingredient_id: str = Field(foreign_key="ingredient.id")
