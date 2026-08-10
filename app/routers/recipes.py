from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models.models import Recipe
from app.schemas.schemas import ScaleRequest, ScaleResponse, CostResponse, ScaleAndCostResponse
from app.services.conversion import scale_recipe, calculate_cost
from typing import List
from app.schemas.schemas import RecipeListItem

router = APIRouter(prefix="/recipes", tags=["recipes"])


def get_recipe_or_404(recipe_id: int, session: Session) -> Recipe:
    recipe = session.get(Recipe, recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe

@router.get("/", response_model=List[RecipeListItem])
def list_recipes(session: Session = Depends(get_session)):
    recipes = session.exec(select(Recipe)).all()
    return recipes

@router.post("/scale", response_model=ScaleResponse)
def scale(request: ScaleRequest, session: Session = Depends(get_session)):
    recipe = get_recipe_or_404(request.recipe_id, session)
    scaled_ingredients = scale_recipe(recipe, request.target_servings, session)

    return ScaleResponse(
        recipe_name=recipe.name,
        target_servings=request.target_servings,
        ingredients=scaled_ingredients,
    )


@router.post("/cost", response_model=CostResponse)
def cost(request: ScaleRequest, session: Session = Depends(get_session)):
    recipe = get_recipe_or_404(request.recipe_id, session)
    total_cost, per_serving = calculate_cost(recipe, request.target_servings, session)

    return CostResponse(
        recipe_name=recipe.name,
        target_servings=request.target_servings,
        total_cost=total_cost,
        cost_per_serving=per_serving,
    )


@router.post("/scale-and-cost", response_model=ScaleAndCostResponse)
def scale_and_cost(request: ScaleRequest, session: Session = Depends(get_session)):
    recipe = get_recipe_or_404(request.recipe_id, session)
    scaled_ingredients = scale_recipe(recipe, request.target_servings, session)
    total_cost, per_serving = calculate_cost(recipe, request.target_servings, session)

    return ScaleAndCostResponse(
        recipe_name=recipe.name,
        target_servings=request.target_servings,
        ingredients=scaled_ingredients,
        total_cost=total_cost,
        cost_per_serving=per_serving,
    )