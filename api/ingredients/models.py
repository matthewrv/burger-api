import uuid

from pydantic import UUID4, BaseModel, Field

__all__ = ("IngredientItem",)


class IngredientItem(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4, serialization_alias="_id")
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
