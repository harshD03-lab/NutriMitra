import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from app.models.food_item import FoodItem
from app.schemas.recommendation import NutrientTargets

FEATURE_COLS = [
    "energy_kcal",
    "protein_g",
    "carbs_g",
    "fat_g",
    "fiber_g",
    "calcium_mg",
    "iron_mg",
    "vitamin_c_mg",
    "vitamin_a_mcg",
    "folate_mcg",
    "zinc_mg",
]

MEAL_CATEGORY_MAP = {
    "breakfast": ["breakfast", "cereal", "milk", "dairy", "eggs"],
    "lunch": ["grains", "pulses", "rice", "vegetables", "meat", "fish", "poultry", "legumes"],
    "dinner": ["soup", "salad", "bread", "roti"],
    "snacks": ["snacks", "fried", "beverages", "fruits", "desserts", "sweets"],
}


def filter_by_meal_type(foods: list[FoodItem], meal_type: str | None) -> list[FoodItem]:
    if not meal_type:
        return foods
    
    meal_type = meal_type.lower()
    if meal_type not in MEAL_CATEGORY_MAP:
        return foods
    
    keywords = MEAL_CATEGORY_MAP[meal_type]
    filtered_foods = []
    
    for food in foods:
        category = (food.category or "").lower().strip()
        matches = False
        for keyword in keywords:
            if keyword in category:
                matches = True
                break
        
        if matches:
            filtered_foods.append(food)
    
    return filtered_foods



def build_feature_matrix(foods: list[FoodItem]) -> np.ndarray:
    records = []
    for f in foods:
        records.append(
            {
                col: getattr(f, col, 0.0) if getattr(f, col, None) is not None else 0.0
                for col in FEATURE_COLS
            }
        )
    return pd.DataFrame(records).fillna(0.0).values


class KNNRecommender:
    def __init__(self, n_neighbors: int = 10):
        self.n_neighbors = n_neighbors
        self.model: NearestNeighbors | None = None
        self.foods: list[FoodItem] = []
        self.feature_matrix: np.ndarray | None = None

    def fit(self, foods: list[FoodItem]):
        self.foods = foods
        self.feature_matrix = build_feature_matrix(foods)
        self.model = NearestNeighbors(
            n_neighbors=min(self.n_neighbors, len(foods)),
            metric="cosine",
        )
        self.model.fit(self.feature_matrix)

    def recommend(
        self,
        targets: NutrientTargets,
        top_k: int = 5,
        meal_type: str | None = None,
    ) -> list[FoodItem]:
        if self.model is None or self.feature_matrix is None:
            return []
        
        filtered_foods = filter_by_meal_type(self.foods, meal_type)
        filtered_foods = filtered_foods[:min(len(filtered_foods), top_k * 2)]
        
        if not filtered_foods:
            return []
        
        filtered_feature_matrix = build_feature_matrix(filtered_foods)
        
        query = np.array(
            [
                [
                    targets.calories,
                    targets.protein_g,
                    targets.carbs_g,
                    targets.fat_g,
                    targets.fiber_g,
                    targets.calcium_mg,
                    targets.iron_mg,
                    0,
                    0,
                    0,
                    0,
                ]
            ]
        )
        
        distances, indices = self.model.kneighbors(query)
        return [filtered_foods[i] for i in indices[0]]
