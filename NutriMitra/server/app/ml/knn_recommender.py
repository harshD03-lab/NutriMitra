import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

from app.ml.meal_slots import MEAL_SLOTS, infer_slots, slot_from_meal_type
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


def filter_by_meal_type(foods: list[FoodItem], meal_type: str | None) -> list[FoodItem]:
    """Return the foods that can be used for a meal slot.

    The dataset's ``category`` column is empty for most rows, so slot
    eligibility comes from the stored ``meal_type`` marker and from the dish
    name (see :func:`app.ml.meal_slots.infer_slots`).
    """
    if not meal_type:
        return foods

    slot = slot_from_meal_type(meal_type) or meal_type
    if slot not in MEAL_SLOTS:
        return foods

    return [food for food in foods if slot in infer_slots(food)]


def build_feature_matrix(foods: list[FoodItem]) -> np.ndarray:
    records = []
    for f in foods:
        records.append(
            {
                col: getattr(f, col, 0.0) if getattr(f, col, None) is not None else 0.0
                for col in FEATURE_COLS
            }
        )
    if not records:
        return np.zeros((0, len(FEATURE_COLS)))
    return pd.DataFrame(records).fillna(0.0).values


class KNNRecommender:
    """Ranks foods by how closely their nutrient profile matches a target."""

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
        if not unique:
            self.model = None
            return
        self.model = NearestNeighbors(
            n_neighbors=min(self.n_neighbors, len(unique)),
            metric="cosine",
        )
        self.model.fit(self.feature_matrix)

    def _query_vector(self, targets: NutrientTargets) -> np.ndarray:
        return np.array(
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

    def rank(
        self, candidates: list[FoodItem], targets: NutrientTargets, top_k: int = 5
    ) -> list[FoodItem]:
        """Rank *candidates* by similarity to *targets*."""
        if not candidates:
            return []
        matrix = build_feature_matrix(candidates)
        model = NearestNeighbors(
            n_neighbors=min(top_k, len(candidates)),
            metric="cosine",
        )
        model.fit(matrix)
        distances, indices = model.kneighbors(self._query_vector(targets))
        return [candidates[i] for i in indices[0]]

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

        if candidates is self.foods:
            distances, indices = self.model.kneighbors(self._query_vector(targets))
            return [self.foods[i] for i in indices[0]]

        return self.rank(candidates, targets, top_k=top_k)
