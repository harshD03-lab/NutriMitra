"""Medical-condition handling for NutriMitra.

The rules implemented here are *general nutrition guidance* derived from the
nutrient values that actually exist in the dataset (energy, protein, fat,
sugar and sodium per 100 g).  They are not medical advice and the module
never claims to diagnose, treat or cure a condition - it only removes foods
that clash with a documented rule and adds a plain-language note to the
plan.

If a condition has no rule that can be evaluated from the dataset, the
condition is reported as "guidance only" instead of being silently ignored.
"""

from dataclasses import dataclass, field

from app.models.food_item import FoodItem

# Documented per-100 g thresholds used by the rules below.
HIGH_SUGAR_G = 15.0
HIGH_SODIUM_MG = 600.0
HIGH_PROTEIN_G = 20.0
HIGH_FAT_G = 20.0


@dataclass
class ConditionRule:
    """A single condition rule.

    ``exclude`` returns True when the food clashes with the rule.
    ``guidance`` is the general, non-diagnostic note shown with the plan.
    ``evaluable`` is False when the dataset has no field the rule needs, in
    which case the condition is only reported as guidance.
    """

    name: str
    guidance: str
    exclude: object = None
    evaluable: bool = True
    note: str = ""


def _diabetes(food: FoodItem) -> bool:
    return (food.sugar_g or 0.0) > HIGH_SUGAR_G


def _hypertension(food: FoodItem) -> bool:
    return (food.sodium_mg or 0.0) > HIGH_SODIUM_MG


def _kidney_disease(food: FoodItem) -> bool:
    return (food.protein_g or 0.0) > HIGH_PROTEIN_G


def _heart_disease(food: FoodItem) -> bool:
    return (food.sodium_mg or 0.0) > HIGH_SODIUM_MG or (food.fat_g or 0.0) > HIGH_FAT_G


def _acid_reflux(food: FoodItem) -> bool:
    return (food.fat_g or 0.0) > HIGH_FAT_G


CONDITION_RULES: dict[str, ConditionRule] = {
    "diabetes": ConditionRule(
        name="diabetes",
        guidance="Plan is lower in sugar; pair it with your own glucose-monitoring advice.",
        exclude=_diabetes,
    ),
    "pcos": ConditionRule(
        name="pcos",
        guidance="Plan is lower in sugar; pair it with your own glucose-monitoring advice.",
        exclude=_diabetes,
    ),
    "hypertension": ConditionRule(
        name="hypertension",
        guidance="Plan keeps sodium low; check your own blood-pressure targets with your doctor.",
        exclude=_hypertension,
    ),
    "kidney_disease": ConditionRule(
        name="kidney_disease",
        guidance="Plan keeps protein moderate; your doctor should set the exact target.",
        exclude=_kidney_disease,
    ),
    "heart_disease": ConditionRule(
        name="heart_disease",
        guidance="Plan keeps sodium and fat moderate; confirm limits with your doctor.",
        exclude=_heart_disease,
    ),
    "acid_reflux": ConditionRule(
        name="acid_reflux",
        guidance="Plan keeps fat moderate; adjust to your own trigger foods.",
        exclude=_acid_reflux,
    ),
    "anemia": ConditionRule(
        name="anemia",
        guidance="Prefer iron rich foods such as green leafy vegetables, jaggery, dates and sesame.",
        exclude=None,
        evaluable=False,
        note="No hard rule - iron content varies too much between records to filter on.",
    ),
    "thyroid": ConditionRule(
        name="thyroid",
        guidance="Raw cruciferous vegetables and soy are usually advised in moderation - check with your doctor.",
        exclude=None,
        evaluable=False,
        note="No hard rule - cooking method and iodine content are not in the dataset.",
    ),
}

# Historical tag based rules kept for datasets that carry a "suitable_for"
# column.  They are applied on top of the nutrient rules above.
RESTRICTIONS: dict[str, list[str]] = {
    "diabetes": ["high_sugar", "high_carbs"],
    "hypertension": ["high_sodium"],
    "kidney_disease": ["high_protein", "high_potassium", "high_phosphorus"],
    "pcos": ["high_sugar", "high_carbs"],
    "heart_disease": ["high_saturated_fat", "high_sodium", "high_cholesterol"],
    "acid_reflux": ["high_fat", "spicy", "acidic"],
    "anemia": [],
    "thyroid": ["goitrogenic_raw"],
}


def parse_conditions(conditions: str | None) -> list[str]:
    """Split a free text condition list into canonical condition names."""
    parsed: list[str] = []
    if not conditions:
        return parsed
    for raw in conditions.split(","):
        cond = raw.strip().lower().replace(" ", "_").replace("-", "_")
        if not cond:
            continue
        if cond in CONDITION_RULES:
            parsed.append(cond)
        elif cond not in parsed:
            parsed.append(cond)
    return parsed


def get_restriction_tags(conditions: str | None) -> set[str]:
    """Restriction tags applied to the dataset's own ``suitable_for`` column."""
    tags: set[str] = set()
    for cond in parse_conditions(conditions):
        tags.update(RESTRICTIONS.get(cond, []))
    return tags


def apply_medical_rules(
    foods: list[FoodItem], conditions: str | None
) -> tuple[list[FoodItem], list[str]]:
    """Filter foods against the medical conditions and return guidance notes.

    Returns the kept foods plus a list of plain-language notes describing what
    was applied and what could not be evaluated from the dataset.
    """
    notes: list[str] = []
    parsed = parse_conditions(conditions)
    if not parsed:
        return foods, notes

    kept = list(foods)
    for cond in parsed:
        rule = CONDITION_RULES.get(cond)
        if rule is None:
            notes.append(
                f"'{cond.replace('_', ' ')}' is not a condition NutriMitra has a rule for, "
                "so no food was filtered for it."
            )
            continue
        if rule.exclude is None:
            notes.append(f"{rule.guidance} (guidance only - {rule.note})")
            continue
        before = len(kept)
        kept = [f for f in kept if not rule.exclude(f)]
        removed = before - len(kept)
        notes.append(
            f"{rule.guidance} {removed} food(s) clashing with this rule were removed."
        )
    return kept, notes
