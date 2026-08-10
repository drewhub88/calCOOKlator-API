from sqlmodel import Session
from app.database import engine, create_db_and_tables
from app.models.models import Recipe, Ingredient, UnitConversion
from test_conversion import session

def seed():
    create_db_and_tables()

    with Session(engine) as session:
        conversions = [
            UnitConversion(unit_type="volume", unit_name="tsp", base_factor=4.92892),
            UnitConversion(unit_type="volume", unit_name="tbsp", base_factor=14.7868),
            UnitConversion(unit_type="volume", unit_name="cup", base_factor=236.588),
            UnitConversion(unit_type="volume", unit_name="L", base_factor=1000.0),
            UnitConversion(unit_type="weight", unit_name="g", base_factor=1.0),
            UnitConversion(unit_type="weight", unit_name="kg", base_factor=1000.0),
        ]
        session.add_all(conversions)

        new_recipe = Recipe(name="Garlic Potatoes", base_servings=5)
        session.add(new_recipe)
        session.commit()
        session.refresh(new_recipe)

        new_ingredients = [
            Ingredient(recipe_id=new_recipe.id, name="Potatoes", quantity=1,
                       unit="kg", unit_type="weight", cost_per_unit=0.5),
            Ingredient(recipe_id=new_recipe.id, name="Garlic", quantity=3,
                       unit="clove", unit_type="count", cost_per_unit=0.10),
            Ingredient(recipe_id=new_recipe.id, name="Olive Oil", quantity=4,
                       unit="tbsp", unit_type="volume", cost_per_unit=0.05),
        ]
        session.add_all(new_ingredients)
        session.commit()

        new_recipe2 = Recipe(name="Tomato Basil Pasta", base_servings=4)
        session.add(new_recipe2)
        session.commit()
        session.refresh(new_recipe2)

        pasta_ingredients = [
            Ingredient(recipe_id=new_recipe2.id, name="Olive Oil", quantity=2,
                         unit="tbsp", unit_type="volume", cost_per_unit=0.05),
             Ingredient(recipe_id=new_recipe2.id, name="Crushed Tomatoes", quantity=400,
                         unit="g", unit_type="weight", cost_per_unit=0.004),
             Ingredient(recipe_id=new_recipe2.id, name="Garlic", quantity=2,
                         unit="clove", unit_type="count", cost_per_unit=0.10),
             Ingredient(recipe_id=new_recipe2.id, name="Basil", quantity=1,
                         unit="tbsp", unit_type="volume", cost_per_unit=0.15),
]
        session.add_all(pasta_ingredients)
        session.commit()
    print("Database seeded successfully.")

if __name__ == "__main__":
    seed()