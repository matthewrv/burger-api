import json

from app.app import app

# load once on application start
with open("assets/ingredients.json") as f:
    ingredients_response = json.load(f)


@app.get("/api/ingredients")
async def get_ingredients():
    return ingredients_response
