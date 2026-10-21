from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    age: int | None = None
    gender: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    activity_level: str | None = None
    diet_type: str | None = None
    medical_conditions: str | None = None
    allergies: str | None = None


class UserUpdate(BaseModel):
    """Profile fields a user may change on the dashboard."""

    name: str | None = None
    age: int | None = None
    gender: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    activity_level: str | None = None
    diet_type: str | None = None
    medical_conditions: str | None = None
    allergies: str | None = None

    model_config = {"extra": "forbid"}


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    age: int | None = None
    gender: str | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    activity_level: str | None = None
    diet_type: str | None = None
    medical_conditions: str | None = None
    allergies: str | None = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
