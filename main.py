import json

from fastapi import FastAPI
from fastapi.middleware import cors

from config import settings

app = FastAPI()
app.add_middleware(cors.CORSMiddleware, allow_origins=settings.allow_origins)

# load once on application start
with open("assets/ingredients.json") as f:
    ingredients_response = json.load(f)


@app.get("/api/ingredients")
async def get_ingredients():
    return ingredients_response
