from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # или укажите название фронтенд сайта
    allow_credentials=True,
    allow_methods=["*"],  # разрешить все методы, включая OPTIONS
    allow_headers=["*"],
)

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = "recipesdb"
client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]

class IngredientItem(BaseModel):
    amount: str
    name: str
    description: Optional[str] = None

class IngredientGroup(BaseModel):
    group: str
    items: List[IngredientItem]

class Step(BaseModel):
    number: int
    title: str
    description: str
    image: Optional[str] = None

class RecipeOut(BaseModel):
    id: str = Field(alias="_id")
    title: str
    subtitle: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    servings: Optional[str] = None
    cook_time: Optional[str] = None
    difficulty: Optional[str] = None
    image: Optional[str] = None
    ingredients: List[IngredientGroup]
    steps: List[Step]
    tips: Optional[List[str]] = None

class LogEntry(BaseModel):
    user_id: Optional[str] = None
    recipe_id: str
    action: str
    step_index: Optional[int] = None
    entry_datetime: datetime = Field(default_factory=datetime.utcnow)

class Rating(BaseModel):
    user_id: Optional[str] = None
    recipe_id: str
    feedback: str
    rating: Optional[int] = None
    entry_datetime: datetime = Field(default_factory=datetime.utcnow)

@app.get("/recipes", response_model=List[RecipeOut])
async def get_recipes():
    cursor = db.recipes.find({})
    recipes = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        recipes.append(doc)
    return recipes

@app.post("/log")
async def log_action(entry: LogEntry):
    data = entry.dict()
    await db.logs.insert_one(data)
    return {"status": "ok"}

@app.post("/rating")
async def log_rating(entry: Rating):
    data = entry.dict()
    await db.logs.insert_one(data)
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return "<h1>Recipe API is running</h1>"