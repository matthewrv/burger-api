"""
Loads default ingredients into database from assets file.
"""

import json
from typing import Any

from sqlmodel import Session

from db import Ingredient, SQLModel
from db.db import connect_to_db


def transform_to_db_model(json_model: dict[str, Any]) -> Ingredient:
    kwargs = json_model.copy()
    kwargs.pop("_id", None)
    return Ingredient(**kwargs)


def main() -> None:
    with open("assets/ingredients.json") as f:
        data = json.load(f)

    engine = connect_to_db()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        ingredients = [transform_to_db_model(ingredient) for ingredient in data["data"]]
        session.add_all(ingredients)
        session.commit()


if __name__ == "__main__":
    main()
