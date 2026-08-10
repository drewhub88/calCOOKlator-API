from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    base_servings: int
    ingredients: List["Ingredient"] = Relationship(back_populates="recipe")

class Ingredient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    quantity: float
    unit: str
    unit_type: str
    cost_per_unit: float
    recipe_id: Optional[int] = Field(default=None, foreign_key="recipe.id")
    recipe: Optional["Recipe"] = Relationship(back_populates="ingredients")

class UnitConversion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    unit_type: str
    unit_name: str
    base_factor: float