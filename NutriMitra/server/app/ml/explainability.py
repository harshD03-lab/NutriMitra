from app.models.food_item import FoodItem
from app.schemas.recommendation import NutrientTargets


def explain_recommendation(
    food: FoodItem,
    targets: NutrientTargets,
) -> str:
    parts = []
    if food.protein_g and food.energy_kcal:
        protein_ratio = food.protein_g / food.energy_kcal * 100
        parts.append(f"{protein_ratio:.1f}% protein by calorie")
    if food.fiber_g and food.fiber_g > 3:
        parts.append("good source of fibre")
    if food.calcium_mg and food.calcium_mg > 100:
        parts.append("rich in calcium")
    return f"{food.name}: " + "; ".join(parts) if parts else food.name
