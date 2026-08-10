from pydantic import BaseModel
from typing import List

class RecipeListItem(BaseModel):
    id: int
    name: str
    base_servings: int

class ScaleRequest(BaseModel):
    recipe_id: int
    target_servings: int


class IngredientOut(BaseModel):
    name: str
    quantity: float
    unit: str


class ScaleResponse(BaseModel):
    recipe_name: str
    target_servings: int
    ingredients: List[IngredientOut]


class CostResponse(BaseModel):
    recipe_name: str
    target_servings: int
    total_cost: float
    cost_per_serving: float


class ScaleAndCostResponse(BaseModel):
    recipe_name: str
    target_servings: int
    ingredients: List[IngredientOut]
    total_cost: float
    cost_per_serving: float