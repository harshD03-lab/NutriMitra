from pydantic import BaseModel

from app.schemas.recommendation import MealPlan


class PlanSummary(BaseModel):
    id: int
    total_calories: float | None = None
    total_protein: float | None = None
    total_carbs: float | None = None
    total_fat: float | None = None
    item_count: int = 0
    created_at: str | None = None


class PlanOut(BaseModel):
    id: int
    meal_plan: list[MealPlan]
    total_calories: float | None = None
    total_protein: float | None = None
    total_carbs: float | None = None
    total_fat: float | None = None
    created_at: str | None = None
