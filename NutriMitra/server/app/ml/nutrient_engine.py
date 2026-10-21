"""Energy and macro target calculation.

Energy needs are estimated with the Mifflin-St Jeor equation followed by a
physical activity factor.  The result is an *estimate* used to size the meal
plan - it is not a medical prescription and the API never reports it as a
guaranteed requirement.
"""

from app.schemas.recommendation import NutrientTargets

SUPPORTED_GENDERS = ("male", "female")

ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

# Reasonable physiological bounds - anything outside is treated as invalid
# input rather than being silently clamped.
MIN_AGE, MAX_AGE = 10, 100
MIN_HEIGHT_CM, MAX_HEIGHT_CM = 100, 250
MIN_WEIGHT_KG, MAX_WEIGHT_KG = 25, 250

BALANCED_MACRO_SPLIT = {"protein": 0.20, "fat": 0.25, "carbs": 0.55}
LOW_CARB_SPLIT = {"protein": 0.30, "fat": 0.40, "carbs": 0.30}
HIGH_PROTEIN_SPLIT = {"protein": 0.35, "fat": 0.25, "carbs": 0.40}

# Diet types that only change *which* foods may be used keep the balanced
# macro split; the split is decided by the macro style of the diet.
MACRO_STYLE_BY_DIET = {
    "low-carb": "low_carb",
    "keto": "low_carb",
    "low_carb": "low_carb",
    "high-protein": "high_protein",
    "high_protein": "high_protein",
}


class NutrientCalculationError(ValueError):
    """Raised when the profile cannot be turned into nutrient targets."""


def _validate_gender(gender: str) -> str:
    value = (gender or "").strip().lower()
    if value not in SUPPORTED_GENDERS:
        raise NutrientCalculationError(
            f"Unsupported gender '{gender}'. Supported values are: "
            f"{', '.join(SUPPORTED_GENDERS)}."
        )
    return value


def _validate_activity(activity_level: str) -> str:
    value = (activity_level or "").strip().lower()
    if value not in ACTIVITY_FACTORS:
        raise NutrientCalculationError(
            f"Unsupported activity level '{activity_level}'. Supported values are: "
            f"{', '.join(sorted(ACTIVITY_FACTORS))}."
        )
    return value


def _validate_range(name: str, value: float, minimum: float, maximum: float) -> float:
    if value is None:
        raise NutrientCalculationError(f"{name} is required.")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise NutrientCalculationError(f"{name} must be a number.") from None
    if number != number or number in (float("inf"), float("-inf")):
        raise NutrientCalculationError(f"{name} must be a finite number.")
    if number < minimum or number > maximum:
        raise NutrientCalculationError(
            f"{name} must be between {minimum:g} and {maximum:g} (got {number:g})."
        )
    return number


def calculate_bmr(weight_kg: float, height_cm: float, age: float, gender: str) -> float:
    """Mifflin-St Jeor basal metabolic rate (kcal/day)."""
    gender = _validate_gender(gender)
    weight = _validate_range("Weight", weight_kg, MIN_WEIGHT_KG, MAX_WEIGHT_KG)
    height = _validate_range("Height", height_cm, MIN_HEIGHT_CM, MAX_HEIGHT_CM)
    years = _validate_range("Age", age, MIN_AGE, MAX_AGE)
    if gender == "male":
        return 10 * weight + 6.25 * height - 5 * years + 5
    return 10 * weight + 6.25 * height - 5 * years - 161


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Basal metabolic rate scaled by the physical activity factor."""
    activity = _validate_activity(activity_level)
    return bmr * ACTIVITY_FACTORS[activity]


def get_macro_split(diet_type: str | None) -> dict[str, float]:
    style = MACRO_STYLE_BY_DIET.get((diet_type or "").strip().lower())
    if style == "low_carb":
        return LOW_CARB_SPLIT
    if style == "high_protein":
        return HIGH_PROTEIN_SPLIT
    return BALANCED_MACRO_SPLIT


def derive_nutrient_targets(
    weight_kg: float,
    height_cm: float,
    age: float,
    gender: str,
    activity_level: str,
    diet_type: str | None = None,
) -> NutrientTargets:
    """Estimated daily energy and macro targets for a profile."""
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    split = get_macro_split(diet_type)
    return NutrientTargets(
        calories=round(tdee, 0),
        protein_g=round(tdee * split["protein"] / 4, 1),
        carbs_g=round(tdee * split["carbs"] / 4, 1),
        fat_g=round(tdee * split["fat"] / 9, 1),
        fiber_g=round(float(weight_kg) * 0.3, 1),
        calcium_mg=1000.0,
        iron_mg=18.0 if gender.strip().lower() == "female" else 10.0,
    )


def scale_targets(targets: NutrientTargets, share: float) -> NutrientTargets:
    """Scale the daily targets down to a single meal slot."""
    return NutrientTargets(
        calories=round(targets.calories * share, 1),
        protein_g=round(targets.protein_g * share, 1),
        carbs_g=round(targets.carbs_g * share, 1),
        fat_g=round(targets.fat_g * share, 1),
        fiber_g=round(targets.fiber_g * share, 1),
        calcium_mg=round(targets.calcium_mg * share, 1),
        iron_mg=round(targets.iron_mg * share, 1),
    )
