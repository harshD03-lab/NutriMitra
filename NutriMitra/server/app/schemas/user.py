from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str
    name: str
    age: int | None = None
    gender: str | None = None
    height_cm: int | None = None
    weight_kg: int | None = None
    activity_level: str | None = None
    diet_type: str | None = None
    medical_conditions: str | None = None


class UserOut(BaseModel):
    id: int
    email: str
    name: str
    age: int | None = None
    gender: str | None = None
    height_cm: int | None = None
    weight_kg: int | None = None
    activity_level: str | None = None
    diet_type: str | None = None
    medical_conditions: str | None = None

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
