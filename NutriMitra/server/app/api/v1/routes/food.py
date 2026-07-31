from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.food_item import FoodItem
from app.schemas.food import FoodListResponse, FoodOut

router = APIRouter(prefix="/food", tags=["food"])


@router.get("/categories", response_model=list[str])
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(FoodItem.category).filter(
        FoodItem.category.isnot(None),
        FoodItem.category != "",
    ).distinct().all()
    return sorted(r[0] for r in rows)


@router.get("/", response_model=FoodListResponse)
def list_foods(
    q: str | None = Query(default=None, description="Search by food name"),
    category: str | None = Query(default=None, description="Filter by food category"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(FoodItem)

    if q:
        pattern = f"%{q.strip()}%"
        query = query.filter(FoodItem.name.ilike(pattern))

    if category:
        query = query.filter(FoodItem.category == category)

    total = query.count()
    items = query.order_by(FoodItem.name).offset(skip).limit(limit).all()

    return FoodListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=[FoodOut.model_validate(i) for i in items],
    )
