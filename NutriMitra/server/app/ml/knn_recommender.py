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
    ) -> list[FoodItem]:
        if self.model is None or self.feature_matrix is None:
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
        distances, indices = self.model.kneighbors(query)
        return [self.foods[i] for i in indices[0]]
