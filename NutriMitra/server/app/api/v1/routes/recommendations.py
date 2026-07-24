from fastapi import APIRouter, Depends

from app.api.v1.routes.users import get_current_user
from app.models.user import User
from app.schemas.recommendation import RecommendationResponse, UserProfile

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("/", response_model=RecommendationResponse)
def generate_plan(profile: UserProfile, current: User = Depends(get_current_user)):
    return RecommendationResponse(
        meal_plan=[],
        total_calories=0,
        total_protein=0,
        total_carbs=0,
        total_fat=0,
        explanation="Not yet implemented",
    )
