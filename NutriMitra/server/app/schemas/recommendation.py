from pydantic import BaseModel


class UserProfile(BaseModel):
    age: int
    gender: str
    height_cm: int
    weight_kg: int
    activity_level: str
    diet_type: str | None = None
    medical_conditions: str | None = None
    target_calories: int | None = None


class MealItem(BaseModel):
    food_name: str
    serving_size: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class MealPlan(BaseModel):
    meal: str
    items: list[MealItem]


class RecommendationResponse(BaseModel):
    meal_plan: list[MealPlan]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    explanation: str | None = None


class NutrientTargets(BaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    calcium_mg: float
    iron_mg: float
