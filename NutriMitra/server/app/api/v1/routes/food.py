from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.food_item import FoodItem

router = APIRouter(prefix="/food", tags=["food"])


@router.get("/")
def list_foods(db: Session = Depends(get_db)):
    items = db.query(FoodItem).limit(50).all()
    return items
