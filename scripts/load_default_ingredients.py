"""
Loads default ingredients into database from assets file.
"""

import json

from sqlmodel import Session, insert

from app.di import connect_to_db
from db import Ingredient, SQLModel


def transform_to_db_model(json_model):
    return Ingredient.model_construct(**json_model, id=json_model["_id"]).model_dump()


def main():
    with open("assets/ingredients.json") as f:
        data = json.load(f)

    ingredients = [transform_to_db_model(ingredient) for ingredient in data["data"]]

    engine = connect_to_db()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        session.exec(insert(Ingredient).values(ingredients))
        session.commit()


if __name__ == "__main__":
    main()
