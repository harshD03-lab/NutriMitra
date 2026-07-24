from sqlalchemy import Column, Float, Integer, String

from app.core.database import Base


class FoodItem(Base):
    __tablename__ = "food_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    category = Column(String, nullable=True)
    energy_kcal = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    fiber_g = Column(Float, nullable=True)
    calcium_mg = Column(Float, nullable=True)
    iron_mg = Column(Float, nullable=True)
    vitamin_c_mg = Column(Float, nullable=True)
    vitamin_a_mcg = Column(Float, nullable=True)
    folate_mcg = Column(Float, nullable=True)
    zinc_mg = Column(Float, nullable=True)
    serving_size_g = Column(Integer, nullable=True)
    suitable_for = Column(String, nullable=True)
