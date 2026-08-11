# 🍳 calCOOKlator

An API (with a simple web UI on top) for scaling recipes to a new serving size, converting quantities into kitchen-friendly units and calculating food cost per serving.
 
Scaling a recipe for 4 people up to 150 for a catering order gets messy fast: 16 tablespoons means nothing to a line cook, and recalculating margins by hand is slow and error-prone. calCOOKlator handles both.

---

## 🚀 Live Demo
 
- **Try it:** `https://calcooklator-api-production.up.railway.app/static/index.html`
- **API docs:** `https://calcooklator-api-production.up.railway.app/docs`

## About This Project
 
A portfolio project covering API design, data modeling, and edge cases that actually matter (unit conversion, rounding, cost accuracy) plus a frontend layer to show the full path from backend logic to a usable tool.

## Features
 
- Scales any recipe to a target serving count
- Converts scaled quantities into sensible kitchen units (16 tbsp → 1 cup), not raw decimals
- Rounds to kitchen-friendly fractions (1/8, 1/4, 1/3, 1/2, 2/3, 3/4)
- Costs off unrounded values so error doesn't compound across ingredients

## Tech Stack
 
FastAPI + SQLModel (SQLite for dev, swappable to Postgres) + Pydantic for validation. Deployed on Render.

## Architecture

```
/app
  /models     -> database table definitions
  /schemas    -> API request/response shapes
  /routers    -> endpoints
  /services   -> scaling, conversion, and costing logic
database.py
main.py
```

## Data Model
 
**recipes** — id, name, base_servings
**ingredients** — id, recipe_id (FK), name, quantity, unit, unit_type, cost_per_unit
**unit_conversions** — id, unit_type, unit_name, base_factor
 
Units convert to a common base (ml for volume, g for weight) before scaling or costing, then convert back to the most kitchen-friendly unit for display.
 
## API Endpoints
 
| Method | Endpoint | Description |
|---|---|---|
| GET  | /recipes/ | List all recipes |
| POST | /recipes/scale | Scale a recipe to a new serving size |
| POST | /recipes/cost | Get total and per-serving cost |
| POST | /recipes/scale-and-cost | Both combined |
 
Full schemas at `/docs`.


## Known Limitations & Design Decisions
 
**No volume-to-weight conversion.** Cups of flour → grams needs ingredient-specific density data (flour, sugar, and water all differ). This API only converts within a unit family — volume↔volume, weight↔weight. A density lookup table per ingredient would be the next step.
 
**Unit conversions are data, not code.** Adding a new unit is a row in `unit_conversions`, not a redeploy.
 
**Rounding fractions are fixed** (1/8, 1/4, 1/3, 1/2, 2/3, 3/4), matching US measuring tools. No metric-friendly rounding (nearest 5g).
 
**No shrinkage/yield adjustment.** Scales raw ingredient quantities only — doesn't account for cooking loss.
 
**Single-recipe scope.** No multi-recipe menus or shared inventory. Each request is stateless.