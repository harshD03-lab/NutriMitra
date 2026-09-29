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
        seen: set[str] = set()
        unique: list[FoodItem] = []
        for f in foods:
            key = (f.name or "").strip().lower()
            if key in seen:
                continue
            seen.add(key)
            unique.append(f)

        self.foods = unique
        self.feature_matrix = build_feature_matrix(unique)
        self.model = NearestNeighbors(
            n_neighbors=min(self.n_neighbors, len(unique)),
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

        candidates = filter_by_meal_type(self.foods, meal_type)
        if not candidates:
            return []

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

        if candidates is self.foods:
            distances, indices = self.model.kneighbors(query)
            return [self.foods[i] for i in indices[0]]

        local_model = NearestNeighbors(
            n_neighbors=min(self.n_neighbors, len(candidates)),
            metric="cosine",
        )
        local_model.fit(build_feature_matrix(candidates))
        distances, indices = local_model.kneighbors(query)
        return [candidates[i] for i in indices[0]]
