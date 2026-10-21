from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """Profile sent by the client when a meal plan is requested.

    Every field is optional: the API falls back to the stored profile of the
    authenticated user and reports a clear error when neither source has the
    information.
    """

    age: int | None = None
    gender: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    activity_level: str | None = None
    diet_type: str | None = None
    medical_conditions: str | None = None
    allergies: str | None = None
    target_calories: int | None = None


class MealItem(BaseModel):
    food_name: str
    serving_size: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class MealTotals(BaseModel):
    """Nutritional totals of a meal, calculated from its items."""

    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0


class MealPlan(BaseModel):
    meal: str
    items: list[MealItem]
    totals: MealTotals = Field(default_factory=MealTotals)


class RecommendationResponse(BaseModel):
    meal_plan: list[MealPlan]
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    # The estimated daily target the plan was built for.  It is an estimate,
    # not a guarantee - the totals above are what the meals actually contain.
    target_calories: float = 0.0
    target_protein_g: float = 0.0
    target_carbs_g: float = 0.0
    target_fat_g: float = 0.0
    explanation: str | None = None


class NutrientTargets(BaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    calcium_mg: float
    iron_mg: float
