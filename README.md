# CookCalc API 🍳
A lightweight Python API that handles recipe scaling and food cost (COGS) calculations using FastAPI and SQLModel.

# Why this exists?
Scaling a recipe for 4 people up to 150 for a catering order sounds simple on paper, but it quickly turns messy in a real kitchen. Texting a line cook to use "16 tablespoons" of an ingredient doesn't mean anything useful, and trying to recalculate profit margins by hand over a Excel sheet is a massive waste of time. 

I built this API to solve that exact back-of-house bottleneck. It automates the scale math, converts the numbers into actual kitchen-friendly tools (like cups or kilograms instead of ugly floats), and calculates the real food cost per serving.


## Known Limitations & Design Decisions

**Volume-to-weight conversion is out of scope.**
Converting between volume and weight units (e.g. cups of flour → grams) 
requires ingredient-specific density data, since flour, sugar, and water 
all have different densities. This API only converts within a unit 
family (volume↔volume, weight↔weight). Adding a density lookup table 
per ingredient is the natural next step if this were extended.

**Unit conversions are stored as data, not code.**
The `unit_conversions` table means adding a new unit (e.g. "fl oz") is 
a data insert, not a redeploy. Tradeoff: less type-safety than an enum, 
more flexibility.

**Rounding uses a fixed set of "kitchen-friendly" fractions** 
(1/8, 1/4, 1/3, 1/2, 2/3, 3/4). This covers standard US measuring tools 
but doesn't attempt metric-friendly rounding (e.g. nearest 5g) — a 
locale-aware rounding strategy would be needed for a production version.

**No ingredient substitution or shrinkage/yield adjustment.**
Real catering math often accounts for cooking loss (e.g. onions losing 
volume when caramelized). This API assumes raw-ingredient scaling only.

**Single-recipe scope.**
No multi-recipe menus, no shared pantry/inventory tracking across 
recipes — each request is stateless and self-contained.