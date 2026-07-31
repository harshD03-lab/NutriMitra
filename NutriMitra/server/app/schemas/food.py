from pydantic import BaseModel


class FoodOut(BaseModel):
    id: int
    name: str
    category: str | None = None
    energy_kcal: float | None = None
    protein_g: float | None = None
    carbs_g: float | None = None
    fat_g: float | None = None
    fiber_g: float | None = None
    calcium_mg: float | None = None
    iron_mg: float | None = None
    vitamin_c_mg: float | None = None
    vitamin_a_mcg: float | None = None
    folate_mcg: float | None = None
    zinc_mg: float | None = None
    serving_size_g: int | None = None
    suitable_for: str | None = None

    model_config = {"from_attributes": True}


class FoodListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[FoodOut]
