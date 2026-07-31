import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.v1.routes.users import get_current_user
from app.core.database import get_db
from app.models.diet_plan import DietPlan
from app.models.user import User
from app.schemas.plan import PlanOut, PlanSummary
from app.schemas.recommendation import MealPlan

router = APIRouter(prefix="/plans", tags=["plans"])


def _load_meal_plan(plan: DietPlan) -> list[MealPlan]:
    try:
        data = json.loads(plan.meal_data)
        return [MealPlan.model_validate(slot) for slot in data]
    except (ValueError, TypeError):
        return []


def _to_summary(plan: DietPlan) -> PlanSummary:
    return PlanSummary(
        id=plan.id,
        total_calories=plan.total_calories,
        total_protein=plan.total_protein,
        total_carbs=plan.total_carbs,
        total_fat=plan.total_fat,
        item_count=sum(len(slot.items) for slot in _load_meal_plan(plan)),
        created_at=plan.created_at,
    )


@router.get("/", response_model=list[PlanSummary])
def list_plans(
    limit: int = Query(default=20, ge=1, le=100),
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plans = (
        db.query(DietPlan)
        .filter(DietPlan.user_id == current.id)
        .order_by(DietPlan.id.desc())
        .limit(limit)
        .all()
    )
    return [_to_summary(p) for p in plans]


@router.get("/{plan_id}", response_model=PlanOut)
def get_plan(
    plan_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = (
        db.query(DietPlan)
        .filter(DietPlan.id == plan_id, DietPlan.user_id == current.id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return PlanOut(
        id=plan.id,
        meal_plan=_load_meal_plan(plan),
        total_calories=plan.total_calories,
        total_protein=plan.total_protein,
        total_carbs=plan.total_carbs,
        total_fat=plan.total_fat,
        created_at=plan.created_at,
    )


@router.delete("/{plan_id}")
def delete_plan(
    plan_id: int,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    plan = (
        db.query(DietPlan)
        .filter(DietPlan.id == plan_id, DietPlan.user_id == current.id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return {"detail": "Plan deleted"}
