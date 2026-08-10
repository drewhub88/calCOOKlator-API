"""
test_conversion.py

Run with: pytest
Tests the core scaling/conversion/rounding/costing logic.
"""

import pytest
from sqlmodel import Session, SQLModel, create_engine
from app.models.models import Recipe, Ingredient, UnitConversion
from app.services.conversion import (
    round_to_nice_fraction,
    to_base_quantity,
    choose_best_display_unit,
    scale_recipe,
    calculate_cost,
)

# Use an in-memory database just for tests — nothing touches your real cookcalc.db
engine = create_engine("sqlite:///:memory:")


@pytest.fixture
def session():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # seed minimal unit conversions needed for tests
        session.add_all([
            UnitConversion(unit_type="volume", unit_name="tsp", base_factor=4.92892),
            UnitConversion(unit_type="volume", unit_name="tbsp", base_factor=14.7868),
            UnitConversion(unit_type="volume", unit_name="cup", base_factor=236.588),
            UnitConversion(unit_type="volume", unit_name="L", base_factor=1000.0),
            UnitConversion(unit_type="weight", unit_name="g", base_factor=1.0),
            UnitConversion(unit_type="weight", unit_name="kg", base_factor=1000.0)
        ])
        session.commit()
        yield session
    SQLModel.metadata.drop_all(engine)


def make_recipe(session, base_servings=4):
    recipe = Recipe(name="Test Recipe", base_servings=base_servings)
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


# ---------- Rounding tests ----------

def test_rounds_to_nearest_third():
    assert round_to_nice_fraction(9.38) == pytest.approx(9 + 1/3, rel=1e-2)


def test_rounds_to_nearest_half():
    assert round_to_nice_fraction(2.51) == pytest.approx(2.5, rel=1e-2)


def test_rounds_up_to_whole_number():
    # 0.95 should round up to 1, not stay as a fraction
    assert round_to_nice_fraction(0.95) == 1


def test_rounds_zero_correctly():
    assert round_to_nice_fraction(0.0) == 0


# ---------- Unit conversion tests ----------

def test_tbsp_to_base_ml(session):
    result = to_base_quantity(4, "tbsp", session)
    assert result == pytest.approx(4 * 14.7868, rel=1e-3)


def test_kg_to_base_g(session):
    result = to_base_quantity(2, "kg", session)
    assert result == pytest.approx(2000.0, rel=1e-3)


def test_choose_best_unit_picks_cup_over_tbsp(session):
    # 250 ml should resolve to "cup" not "tbsp", since cup is the biggest unit still >= 1
    best = choose_best_display_unit(250, "volume", session)
    assert best.unit_name == "cup"


def test_choose_best_unit_falls_back_to_smaller_unit(session):
    # A small amount (10 ml) should NOT resolve to "cup" (that'd be < 1 cup)
    best = choose_best_display_unit(10, "volume", session)
    assert best.unit_name in ("tsp", "tbsp")


# ---------- Scaling tests ----------

def test_scale_up_doubles_quantity(session):
    recipe = make_recipe(session, base_servings=4)
    ingredient = Ingredient(
        recipe_id=recipe.id, name="Olive Oil", quantity=4,
        unit="tbsp", unit_type="volume", cost_per_unit=0.05
    )
    session.add(ingredient)
    session.commit()
    session.refresh(recipe)

    scaled = scale_recipe(recipe, target_servings=8, session=session)  # 2x scale
    # 4 tbsp x2 = 8 tbsp = 118.29 ml, which is still < 1 cup, so should stay in tbsp
    assert scaled[0]["quantity"] == pytest.approx(8, rel=1e-1)


def test_scale_down_halves_quantity(session):
    recipe = make_recipe(session, base_servings=4)
    ingredient = Ingredient(
        recipe_id=recipe.id, name="Flour", quantity=200,
        unit="g", unit_type="weight", cost_per_unit=0.002
    )
    session.add(ingredient)
    session.commit()
    session.refresh(recipe)

    scaled = scale_recipe(recipe, target_servings=2, session=session)  # half scale
    assert scaled[0]["quantity"] == pytest.approx(100, rel=1e-1)


def test_count_type_ingredient_is_not_unit_converted(session):
    recipe = make_recipe(session, base_servings=4)
    ingredient = Ingredient(
        recipe_id=recipe.id, name="Garlic", quantity=3,
        unit="clove", unit_type="count", cost_per_unit=0.10
    )
    session.add(ingredient)
    session.commit()
    session.refresh(recipe)

    scaled = scale_recipe(recipe, target_servings=8, session=session)  # 2x
    assert scaled[0]["quantity"] == pytest.approx(6, rel=1e-2)
    assert scaled[0]["unit"] == "clove"


# ---------- Costing tests ----------

def test_cost_scales_correctly(session):
    recipe = make_recipe(session, base_servings=4)
    ingredient = Ingredient(
        recipe_id=recipe.id, name="Flour", quantity=200,
        unit="g", unit_type="weight", cost_per_unit=0.002  # $0.002 per gram
    )
    session.add(ingredient)
    session.commit()
    session.refresh(recipe)

    total, per_serving = calculate_cost(recipe, target_servings=8, session=session)
    # 200g x2 scale = 400g x $0.002/g = $0.80 total
    assert total == pytest.approx(0.80, rel=1e-2)
    assert per_serving == pytest.approx(0.10, rel=1e-2)


def test_cost_uses_unrounded_values_not_display_rounded(session):
    # This test protects against the classic bug: costing off the
    # ROUNDED display quantity instead of the raw scaled quantity,
    # which would compound error across many ingredients.
    recipe = make_recipe(session, base_servings=3)
    ingredient = Ingredient(
        recipe_id=recipe.id, name="Sugar", quantity=333,
        unit="g", unit_type="weight", cost_per_unit=0.001
    )
    session.add(ingredient)
    session.commit()
    session.refresh(recipe)

    total, _ = calculate_cost(recipe, target_servings=1, session=session)
    # scale factor = 1/3, so raw = 111g exactly, cost = 111 * 0.001 = 0.111 -> rounds to 0.11
    assert total == pytest.approx(0.11, rel=1e-2)