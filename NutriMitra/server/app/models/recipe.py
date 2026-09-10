from sqlalchemy import Column, Integer, String, Text, ForeignKey

from app.core.database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey("food_items.id"), nullable=True, index=True)
    cuisine = Column(String, nullable=True)
    cooking_time_mins = Column(Integer, nullable=True)
    instructions = Column(Text, nullable=True)
    ingredients = Column(Text, nullable=True)
