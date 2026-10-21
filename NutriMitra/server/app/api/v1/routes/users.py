from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.ml.hard_filter import SUPPORTED_DIET_TYPES, UnsupportedDietTypeError, normalise_diet_type
from app.ml.nutrient_engine import (
    ACTIVITY_FACTORS,
    MAX_AGE,
    MAX_HEIGHT_CM,
    MAX_WEIGHT_KG,
    MIN_AGE,
    MIN_HEIGHT_CM,
    MIN_WEIGHT_KG,
    SUPPORTED_GENDERS,
)
from app.models.user import User
from app.schemas.user import UserOut, UserUpdate
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

router = APIRouter(prefix="/users", tags=["users"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = int(payload.get("sub"))
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _validate_profile_update(payload: UserUpdate) -> None:
    if payload.age is not None and not (MIN_AGE <= payload.age <= MAX_AGE):
        raise HTTPException(
            status_code=422,
            detail=f"Age must be between {MIN_AGE} and {MAX_AGE}.",
        )
    if payload.gender is not None:
        if payload.gender.strip().lower() not in SUPPORTED_GENDERS:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Unsupported gender '{payload.gender}'. Supported values are: "
                    f"{', '.join(SUPPORTED_GENDERS)}."
                ),
            )
    if payload.height_cm is not None and not (
        MIN_HEIGHT_CM <= payload.height_cm <= MAX_HEIGHT_CM
    ):
        raise HTTPException(
            status_code=422,
            detail=f"Height must be between {MIN_HEIGHT_CM} and {MAX_HEIGHT_CM} cm.",
        )
    if payload.weight_kg is not None and not (
        MIN_WEIGHT_KG <= payload.weight_kg <= MAX_WEIGHT_KG
    ):
        raise HTTPException(
            status_code=422,
            detail=f"Weight must be between {MIN_WEIGHT_KG} and {MAX_WEIGHT_KG} kg.",
        )
    if payload.activity_level is not None:
        if payload.activity_level.strip().lower() not in ACTIVITY_FACTORS:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Unsupported activity level '{payload.activity_level}'. Supported "
                    f"values are: {', '.join(sorted(ACTIVITY_FACTORS))}."
                ),
            )
    if payload.diet_type:
        try:
            normalise_diet_type(payload.diet_type)
        except UnsupportedDietTypeError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/me", response_model=UserOut)
def read_current_user(current: User = Depends(get_current_user)):
    return current


@router.patch("/me", response_model=UserOut)
def update_current_user(
    payload: UserUpdate,
    current: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save the profile the user edited on the dashboard."""
    _validate_profile_update(payload)

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        if isinstance(value, str):
            value = value.strip() or None
        setattr(current, field, value)

    try:
        db.commit()
    except Exception as exc:  # pragma: no cover - defensive
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Your profile could not be saved. Please try again.",
        ) from exc
    db.refresh(current)
    return current
