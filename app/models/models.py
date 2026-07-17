from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class recipe(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    base_servings: int
    ingredients: List["ingredient"] = Relationship(back_populates="recipe")

class ingredient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    quantity: float
    unit: str
    unit_type: str 
    cost_per_unit: float
    recipe_id: Optional[recipe] = Relationship(back_populates="ingredients")

class unit_conversions(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    unit_type: str  # Volume || Weight
    unit_name: str  # tbsp, cup, g, kg, etc.
    base_factor: float  # multiplier to convert to base unit (ml || g)