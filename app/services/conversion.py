from sqlmodel import Session, select
from app.models.models import UnitConversion

# Nice fractions to round to, for kitchen-friendly display
NICE_FRACTIONS = [0, 1/8, 1/4, 1/3, 1/2, 2/3, 3/4, 1]


def get_conversion_factor(unit_name: str, session: Session) -> float:
    """Look up how many base units (ml or g) 1 of this unit equals."""
    result = session.exec(
        select(UnitConversion).where(UnitConversion.unit_name == unit_name)
    ).first()
    if result is None:
        # "count" units like "clove" or "piece" don't convert — treat as base unit of 1
        return 1.0
    return result.base_factor


def get_units_for_type(unit_type: str, session: Session):
    """Get all units of a given type (volume/weight), sorted smallest to largest."""
    results = session.exec(
        select(UnitConversion).where(UnitConversion.unit_type == unit_type)
    ).all()
    return sorted(results, key=lambda u: u.base_factor)


def to_base_quantity(quantity: float, unit: str, session: Session) -> float:
    """Convert a quantity in any unit to its base unit (ml or g)."""
    factor = get_conversion_factor(unit, session)
    return quantity * factor


def choose_best_display_unit(base_qty: float, unit_type: str, session: Session):
    """
    Pick the biggest unit where the converted quantity is still >= 1.
    Returns the UnitConversion row (has .unit_name and .base_factor).
    """
    units = get_units_for_type(unit_type, session)
    if not units:
        return None  # e.g. "count" type has no conversion table entry

    best = units[0]
    for unit in units:
        converted = base_qty / unit.base_factor
        if converted >= 1:
            best = unit
        else:
            break
    return best


def round_to_nice_fraction(qty: float) -> float:
    """Snap a quantity's decimal part to the nearest common kitchen fraction."""
    whole = int(qty)
    decimal = qty - whole

    closest = min(NICE_FRACTIONS, key=lambda f: abs(f - decimal))

    if closest == 1:
        return whole + 1
    return whole + closest


def scale_and_convert_ingredient(ingredient, scale_factor: float, session: Session):
    """
    Takes one Ingredient row + a scale factor, returns a dict with the
    scaled, converted, rounded quantity ready for display, plus the raw
    base quantity (used separately for accurate costing).
    """
    raw_scaled_qty = ingredient.quantity * scale_factor

    if ingredient.unit_type == "count":
        # Whole items (e.g. "clove", "egg") don't get unit-converted, just scaled + rounded
        return {
            "name": ingredient.name,
            "quantity": round(raw_scaled_qty, 2),
            "unit": ingredient.unit,
            "base_quantity_for_costing": raw_scaled_qty,
        }

    base_qty = to_base_quantity(raw_scaled_qty, ingredient.unit, session)
    best_unit = choose_best_display_unit(base_qty, ingredient.unit_type, session)

    if best_unit is None:
        display_qty = raw_scaled_qty
        display_unit_name = ingredient.unit
    else:
        display_qty = base_qty / best_unit.base_factor
        display_unit_name = best_unit.unit_name

    rounded_qty = round_to_nice_fraction(display_qty)

    return {
        "name": ingredient.name,
        "quantity": rounded_qty,
        "unit": display_unit_name,
        "base_quantity_for_costing": base_qty,
    }


def scale_recipe(recipe, target_servings: int, session: Session):
    """Scale every ingredient in a recipe to the target serving size."""
    scale_factor = target_servings / recipe.base_servings
    return [
        scale_and_convert_ingredient(ing, scale_factor, session)
        for ing in recipe.ingredients
    ]


def calculate_cost(recipe, target_servings: int, session: Session):
    """
    Calculate total and per-serving cost.
    IMPORTANT: costs off the raw (unrounded) base quantity, not the
    rounded display quantity, to avoid compounding rounding errors.
    """
    scale_factor = target_servings / recipe.base_servings
    total_cost = 0.0

    for ing in recipe.ingredients:
        raw_scaled_qty = ing.quantity * scale_factor

        if ing.unit_type == "count":
            base_qty = raw_scaled_qty
        else:
            base_qty = to_base_quantity(raw_scaled_qty, ing.unit, session)

        total_cost += base_qty * ing.cost_per_unit

    per_serving = total_cost / target_servings
    return round(total_cost, 2), round(per_serving, 2)