"""Food filtering for NutriMitra.

Three independent filters are applied to the dataset:

* **diet type** - vegetarian / vegan / non-vegetarian rules,
* **allergies** - foods whose name shows they contain a declared allergen,
* **medical conditions** - see :mod:`app.ml.medical_rules`.

Every filter is explicit: when a filter removes everything the caller is told
so, instead of receiving an empty plan that looks like a success.
"""

from app.ml.diet_rules import (
    allergen_tokens,
    classify_food,
    food_matches_allergens,
    normalise_allergens,
)
from app.ml.medical_rules import apply_medical_rules, get_restriction_tags
from app.models.food_item import FoodItem

# Diet types that restrict which foods may be used.
VEGETARIAN = "vegetarian"
VEGAN = "vegan"
NON_VEGETARIAN = "non-vegetarian"

# Diet types the application understands.  The macro styles (balanced,
# low-carb, high-protein) change the macro split only - they do not remove
# any food.
SUPPORTED_DIET_TYPES: dict[str, str | None] = {
    "vegetarian": VEGETARIAN,
    "veg": VEGETARIAN,
    "vegan": VEGAN,
    "non-vegetarian": NON_VEGETARIAN,
    "non vegetarian": NON_VEGETARIAN,
    "non-vegetarian": NON_VEGETARIAN,
    "non_vegetarian": NON_VEGETARIAN,
    "nonveg": NON_VEGETARIAN,
    "non veg": NON_VEGETARIAN,
    "omnivore": NON_VEGETARIAN,
    "non-veg": NON_VEGETARIAN,
    "balanced": None,
    "low-carb": None,
    "low_carb": None,
    "keto": None,
    "high-protein": None,
    "high_protein": None,
}


class UnsupportedDietTypeError(ValueError):
    """Raised when the requested diet type is not supported."""


def normalise_diet_type(diet_type: str | None) -> str | None:
    """Map a user supplied diet type onto a supported rule.

    Returns the diet rule (``vegetarian`` / ``vegan`` / ``non-vegetarian``)
    or ``None`` when the diet type does not restrict foods.
    """
    if diet_type is None:
        return None
    value = diet_type.strip().lower()
    if not value:
        return None
    if value not in SUPPORTED_DIET_TYPES:
        raise UnsupportedDietTypeError(
            f"Unsupported diet type '{diet_type}'. Supported values are: "
            f"{', '.join(sorted(set(SUPPORTED_DIET_TYPES)))}."
        )
    return SUPPORTED_DIET_TYPES[value]


def hard_filter(foods: list[FoodItem], conditions: str | None) -> list[FoodItem]:
    """Remove foods the dataset itself flags as unsuitable for a condition."""
    restricted_tags = get_restriction_tags(conditions)
    if not restricted_tags:
        return foods
    return [
        f
        for f in foods
        if not (f.suitable_for and any(tag in f.suitable_for for tag in restricted_tags))
    ]


def filter_by_diet(foods: list[FoodItem], diet_rule: str | None) -> list[FoodItem]:
    """Apply the vegetarian / vegan / non-vegetarian rules."""
    if not diet_rule or diet_rule == NON_VEGETARIAN:
        return list(foods)
    kept: list[FoodItem] = []
    for food in foods:
        info = classify_food(food.name, food.is_veg)
        if not info["is_vegetarian"]:
            continue
        if diet_rule == VEGAN and (info["is_dairy"] or info["is_honey"]):
            continue
        kept.append(food)
    return kept


def filter_by_allergies(
    foods: list[FoodItem], allergies: str | None
) -> tuple[list[FoodItem], set[str], list[str]]:
    """Remove foods that contain a declared allergen.

    Returns the kept foods, the allergens that could be applied and the
    allergen terms that could not be mapped (so they can be reported).
    """
    supported, unsupported = normalise_allergens(allergies)
    if not supported:
        return list(foods), supported, unsupported
    tokens = allergen_tokens(supported)
    kept = [f for f in foods if not food_matches_allergens(f.name, tokens)]
    return kept, supported, unsupported


def filter_foods(
    foods: list[FoodItem],
    diet_type: str | None = None,
    allergies: str | None = None,
    conditions: str | None = None,
) -> dict:
    """Apply every filter and report what happened.

    The returned dictionary contains the surviving foods, per-stage counts and
    the notes/explanations that should be shown with the plan.
    """
    notes: list[str] = []
    total = len(foods)

    diet_rule = normalise_diet_type(diet_type)
    diet_foods = filter_by_diet(foods, diet_rule)
    if diet_rule == VEGETARIAN:
        notes.append(
            f"Vegetarian plan: {total - len(diet_foods)} meat, fish or egg dish(es) removed."
        )
    elif diet_rule == VEGAN:
        notes.append(
            f"Vegan plan: {total - len(diet_foods)} dish(es) containing animal-derived "
            "ingredients (meat, fish, egg, dairy or honey) removed."
        )

    allergy_foods, applied_allergens, unsupported_allergens = filter_by_allergies(
        diet_foods, allergies
    )
    if applied_allergens:
        removed = len(diet_foods) - len(allergy_foods)
        notes.append(
            f"Allergens applied: {', '.join(sorted(applied_allergens))} "
            f"({removed} matching dish(es) removed)."
        )
    if unsupported_allergens:
        notes.append(
            "No ingredient data is available for: "
            f"{', '.join(unsupported_allergens)}. Review those manually."
        )

    condition_foods, condition_notes = apply_medical_rules(allergy_foods, conditions)
    notes.extend(condition_notes)

    return {
        "foods": condition_foods,
        "notes": notes,
        "diet_rule": diet_rule,
        "applied_allergens": applied_allergens,
        "unsupported_allergens": unsupported_allergens,
        "total": total,
    }
