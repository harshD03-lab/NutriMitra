import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.routes.users import get_current_user
from app.core.database import get_db
from app.ml.explainability import explain_item
from app.ml.hard_filter import (
    UnsupportedDietTypeError,
    filter_foods,
    normalise_diet_type,
)
from app.ml.nutrient_engine import NutrientCalculationError, derive_nutrient_targets
from app.ml.plan_builder import build_meal_plan
from app.models.diet_plan import DietPlan
from app.models.food_item import FoodItem
from app.models.user import User
from app.schemas.recommendation import (
    RecommendationResponse,
    UserProfile,
)

logger = logging.getLogger("nutrimitra")

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Profile fields that must be known before a plan can be built.  The label is
# what the user sees on the dashboard.
REQUIRED_PROFILE_FIELDS: list[tuple[str, str]] = [
    ("age", "age"),
    ("gender", "gender"),
    ("height_cm", "height"),
    ("weight_kg", "weight"),
    ("activity_level", "activity level"),
    ("diet_type", "diet type"),
]


def _effective_profile(profile: UserProfile, current: User) -> dict:
    """Merge the requested profile with the stored one."""
    return {
        "age": profile.age if profile.age is not None else current.age,
        "gender": profile.gender if profile.gender is not None else current.gender,
        "height_cm": (
            profile.height_cm if profile.height_cm is not None else current.height_cm
        ),
        "weight_kg": (
            profile.weight_kg if profile.weight_kg is not None else current.weight_kg
        ),
        "activity_level": (
            profile.activity_level
            if profile.activity_level is not None
            else current.activity_level
        ),
        "diet_type": (
            profile.diet_type if profile.diet_type is not None else current.diet_type
        ),
        "medical_conditions": (
            profile.medical_conditions
            if profile.medical_conditions is not None
            else current.medical_conditions
        ),
        "allergies": (
            profile.allergies if profile.allergies is not None else current.allergies
        ),
    }


@router.post("/", response_model=RecommendationResponse)
def generate_plan(
    profile: UserProfile,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    effective = _effective_profile(profile, current)

    missing = [
        label
        for field, label in REQUIRED_PROFILE_FIELDS
        if effective.get(field) in (None, "")
    ]
    if missing:
        raise HTTPException(
            status_code=422,
            detail=(
                "Missing required profile details: "
                + ", ".join(missing)
                + ". Fill them in on the dashboard and try again."
            ),
        )

    try:
        diet_rule = normalise_diet_type(effective["diet_type"])
    except UnsupportedDietTypeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        targets = derive_nutrient_targets(
            weight_kg=effective["weight_kg"],
            height_cm=effective["height_cm"],
            age=effective["age"],
            gender=effective["gender"],
            activity_level=effective["activity_level"],
            diet_type=effective["diet_type"],
        )
    except NutrientCalculationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    foods = db.query(FoodItem).all()
    if not foods:
        logger.error("Meal plan requested but the food_items table is empty")
        raise HTTPException(
            status_code=503,
            detail=(
                "The nutrition dataset is not loaded on this server, so no meal "
                "plan can be built. Set DATA_DIR to the folder that contains the "
                "dataset CSV files and restart the service."
            ),
        )

    filter_result = filter_foods(
        foods,
        diet_type=effective["diet_type"],
        allergies=effective["allergies"],
        conditions=effective["medical_conditions"],
    )
    filtered_foods = filter_result["foods"]

    if not filtered_foods:
        raise HTTPException(
            status_code=422,
            detail=(
                "No foods match your dietary restrictions. Please relax the diet "
                "type, allergy or medical condition filters and try again."
            ),
        )

    meal_plan, plan_notes = build_meal_plan(filtered_foods, targets)
    if not meal_plan:
        raise HTTPException(
            status_code=500,
            detail="The meal plan could not be built from the available foods.",
        )

    # Totals are calculated from the same records that are shown to the user.
    total_calories = round(sum(slot.totals.calories for slot in meal_plan), 1)
    total_protein = round(sum(slot.totals.protein_g for slot in meal_plan), 1)
    total_carbs = round(sum(slot.totals.carbs_g for slot in meal_plan), 1)
    total_fat = round(sum(slot.totals.fat_g for slot in meal_plan), 1)

    explanations = [
        explain_item(item, targets) for slot in meal_plan for item in slot.items
    ][:8]
    notes = list(filter_result["notes"]) + list(plan_notes)
    explanation = " | ".join(notes + explanations) if (notes or explanations) else None

    diet_plan = DietPlan(
        user_id=current.id,
        meal_data=json.dumps([slot.model_dump() for slot in meal_plan]),
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat,
        created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    db.add(diet_plan)
    try:
        db.commit()
    except Exception as exc:  # pragma: no cover - defensive
        db.rollback()
        logger.error("Could not save the generated meal plan: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="The meal plan could not be saved, so it was not stored. Please try again.",
        ) from exc

    return RecommendationResponse(
        meal_plan=meal_plan,
        total_calories=total_calories,
        total_protein=total_protein,
        total_carbs=total_carbs,
        total_fat=total_fat,
        target_calories=targets.calories,
        target_protein_g=targets.protein_g,
        target_carbs_g=targets.carbs_g,
        target_fat_g=targets.fat_g,
        explanation=explanation,
    )
