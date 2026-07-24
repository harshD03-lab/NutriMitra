import math

from app.schemas.recommendation import NutrientTargets


def calculate_bmr(weight_kg: int, height_cm: int, age: int, gender: str) -> float:
    if gender.lower() == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161


def calculate_tdee(bmr: float, activity_level: str) -> float:
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    return bmr * multipliers.get(activity_level, 1.2)


BALANCED_MACRO_SPLIT = {"protein": 0.20, "fat": 0.25, "carbs": 0.55}
LOW_CARB_SPLIT = {"protein": 0.30, "fat": 0.40, "carbs": 0.30}
HIGH_PROTEIN_SPLIT = {"protein": 0.35, "fat": 0.25, "carbs": 0.40}


def get_macro_split(diet_type: str | None) -> dict[str, float]:
    if diet_type and diet_type.lower() in ("low-carb", "keto", "low_carb"):
        return LOW_CARB_SPLIT
    if diet_type and diet_type.lower() in ("high-protein", "high_protein"):
        return HIGH_PROTEIN_SPLIT
    return BALANCED_MACRO_SPLIT


def derive_nutrient_targets(
    weight_kg: int,
    height_cm: int,
    age: int,
    gender: str,
    activity_level: str,
    diet_type: str | None = None,
) -> NutrientTargets:
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    split = get_macro_split(diet_type)
    return NutrientTargets(
        calories=round(tdee, 0),
        protein_g=round(tdee * split["protein"] / 4, 1),
        carbs_g=round(tdee * split["carbs"] / 4, 1),
        fat_g=round(tdee * split["fat"] / 9, 1),
        fiber_g=round(weight_kg * 0.3, 1),
        calcium_mg=1000.0,
        iron_mg=18.0 if gender.lower() == "female" else 10.0,
    )
