from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.routes.users import get_current_user
from app.core.database import get_db
from app.models.food_item import FoodItem
from app.models.user import User
from app.schemas.recommendation import (
    MealItem,
    MealPlan,
    RecommendationResponse,
    UserProfile,
)
from app.ml.explainability import explain_recommendation
from app.ml.hard_filter import hard_filter
from app.ml.knn_recommender import KNNRecommender
from app.ml.nutrient_engine import derive_nutrient_targets

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

MEAL_CATEGORY_MAP: dict[str, str] = {
    "breakfast": "breakfast",
    "cereal": "breakfast",
    "milk": "breakfast",
    "dairy": "breakfast",
    "eggs": "breakfast",
    "grains": "lunch",
    "pulses": "lunch",
    "rice": "lunch",
    "vegetables": "lunch",
    "meat": "lunch",
    "fish": "lunch",
    "poultry": "lunch",
    "legumes": "lunch",
    "snacks": "snacks",
    "fried": "snacks",
    "beverages": "snacks",
    "fruits": "snacks",
    "desserts": "snacks",
    "sweets": "snacks",
    "soup": "dinner",
    "salad": "dinner",
    "bread": "dinner",
    "roti": "dinner",
}

MEAL_SLOTS = ["breakfast", "lunch", "snacks", "dinner"]


def _resolve(value, fallback, default):
    return value if value is not None else (fallback if fallback is not None else default)


@router.post("/", response_model=RecommendationResponse)
def generate_plan(
    profile: UserProfile,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    foods = db.query(FoodItem).all()
    if not foods:
        return RecommendationResponse(
            meal_plan=[],
            total_calories=0,
            total_protein=0,
            total_carbs=0,
            total_fat=0,
            explanation="No food data available. Import the ICMR-NIN dataset first.",
        )

    targets = derive_nutrient_targets(
        weight_kg=_resolve(profile.weight_kg, current.weight_kg, 70),
        height_cm=_resolve(profile.height_cm, current.height_cm, 170),
        age=_resolve(profile.age, current.age, 30),
        gender=_resolve(profile.gender, current.gender, "male"),
        activity_level=_resolve(profile.activity_level, current.activity_level, "sedentary"),
        diet_type=profile.diet_type or current.diet_type,
    )

    conditions = profile.medical_conditions or current.medical_conditions
    filtered_foods = hard_filter(foods, conditions)

    if not filtered_foods:
        return RecommendationResponse(
            meal_plan=[], total_calories=0, total_protein=0, total_carbs=0, total_fat=0,
            explanation="No foods match your dietary restrictions.",
        )

    recommender = KNNRecommender(n_neighbors=min(16, len(filtered_foods)))
    recommender.fit(filtered_foods)
    recommended = recommender.recommend(targets, top_k=16)

    if not recommended:
        return RecommendationResponse(
            meal_plan=[], total_calories=0, total_protein=0, total_carbs=0, total_fat=0,
            explanation="Could not generate recommendations from available foods.",
        )

    grouped: dict[str, list[MealItem]] = {s: [] for s in MEAL_SLOTS}
    for food in recommended:
        cat = (food.category or "").lower().strip()
        slot = "lunch"
        for keyword, mapped in MEAL_CATEGORY_MAP.items():
            if keyword in cat:
                slot = mapped
                break
        grouped[slot].append(
            MealItem(
                food_name=food.name,
                serving_size=f"{food.serving_size_g or 100}g",
                calories=food.energy_kcal or 0,
                protein_g=food.protein_g or 0,
                carbs_g=food.carbs_g or 0,
                fat_g=food.fat_g or 0,
            )
        )

    meal_plan = [
        MealPlan(meal=s.capitalize(), items=grouped[s])
        for s in MEAL_SLOTS
        if grouped[s]
    ]

    explanations = [explain_recommendation(f, targets) for f in recommended[:5]]

    return RecommendationResponse(
        meal_plan=meal_plan,
        total_calories=round(sum(f.energy_kcal or 0 for f in recommended), 1),
        total_protein=round(sum(f.protein_g or 0 for f in recommended), 1),
        total_carbs=round(sum(f.carbs_g or 0 for f in recommended), 1),
        total_fat=round(sum(f.fat_g or 0 for f in recommended), 1),
        explanation=" | ".join(explanations),
    )
