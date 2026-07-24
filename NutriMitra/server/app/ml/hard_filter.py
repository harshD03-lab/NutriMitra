from app.models.food_item import FoodItem


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


def get_restriction_tags(conditions: str | None) -> set[str]:
    if not conditions:
        return set()
    tags: set[str] = set()
    for cond in conditions.split(","):
        cond = cond.strip().lower()
        tags.update(RESTRICTIONS.get(cond, []))
    return tags


def hard_filter(foods: list[FoodItem], conditions: str | None) -> list[FoodItem]:
    restricted_tags = get_restriction_tags(conditions)
    if not restricted_tags:
        return foods
    return [
        f
        for f in foods
        if not (f.suitable_for and any(tag in f.suitable_for for tag in restricted_tags))
    ]
