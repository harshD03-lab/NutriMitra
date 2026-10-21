from app.models.food_item import FoodItem
from app.schemas.recommendation import MealItem, NutrientTargets


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


def explain_item(item: MealItem, targets: NutrientTargets) -> str:
    """Explain a planned item using the values that are shown to the user."""
    parts = []
    if item.protein_g and item.calories:
        protein_ratio = item.protein_g / item.calories * 100
        parts.append(f"{protein_ratio:.1f}% protein by calorie")
    if item.fat_g and item.calories:
        fat_ratio = item.fat_g * 9 / item.calories * 100
        parts.append(f"{fat_ratio:.0f}% of energy from fat")
    if item.carbs_g and item.calories:
        carb_ratio = item.carbs_g * 4 / item.calories * 100
        parts.append(f"{carb_ratio:.0f}% of energy from carbs")
    if item.protein_g and item.protein_g >= 5:
        parts.append("good protein source")
    return f"{item.food_name} ({item.serving_size}): " + "; ".join(parts)
