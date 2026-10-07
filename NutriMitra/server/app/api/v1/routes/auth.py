from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import LoginRequest, Token, UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        name=payload.name,
        age=payload.age,
        gender=payload.gender,
        height_cm=payload.height_cm,
        weight_kg=payload.weight_kg,
        activity_level=payload.activity_level,
        diet_type=payload.diet_type,
        medical_conditions=payload.medical_conditions,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        print(f"Login attempt for email: {payload.email}")
        user = db.query(User).filter(User.email == payload.email).first()
        print(f"User query result: {user}")
        if not user:
            print(f"User not found for email: {payload.email}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        print(f"Verifying password for user: {user.id}")
        password_valid = verify_password(payload.password, user.hashed_password)
        print(f"Password verification result: {password_valid}")
        if not password_valid:
            print(f"Invalid password for user: {user.id}")
            raise HTTPException(status_code=401, detail="Invalid credentials")
            
        print(f"Creating access token for user: {user.id}")
        token = create_access_token({"sub": str(user.id)})
        print(f"Access token created successfully")
        return Token(access_token=token)
    except HTTPException:
        raise
    except Exception as e:
        # Log the exception for debugging
        print(f"Unexpected error in login: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
