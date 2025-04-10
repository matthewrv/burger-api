from pydantic import BaseModel, Field


class IngredientItem(BaseModel):
    id: str = Field(max_length=255)
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
