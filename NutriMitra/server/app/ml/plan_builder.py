"""Builds a daily meal plan from the filtered dataset.

The builder works slot by slot.  For every slot it

1. takes the foods that are suitable for that slot,
2. ranks them with the nutrient-profile recommender
   (:class:`app.ml.knn_recommender.KNNRecommender`),
3. picks the items whose energy fits the slot budget while preferring foods
   that really belong to that meal, and
4. reports the per meal totals calculated from the very same records.

Nutritional totals are therefore always derived from the food rows that are
displayed - they are never estimated separately.
"""

from app.ml.knn_recommender import KNNRecommender
from app.ml.meal_slots import (
    MEAL_SLOTS,
    SLOT_ITEM_COUNTS,
    SLOT_SHARES,
    specific_slots,
)
from app.ml.nutrient_engine import scale_targets
from app.models.food_item import FoodItem
from app.schemas.recommendation import MealItem, MealPlan, MealTotals, NutrientTargets

# A food is only used when it has a usable energy value.
MIN_USABLE_ENERGY_KCAL = 1.0

# How far over the slot budget a single item may push the meal.
SLOT_OVERSHOOT_TOLERANCE = 1.12

# How many foods are ranked per slot by the nutrient recommender.
POOL_SIZE = 80


def serving_label(food: FoodItem) -> str:
    """Human readable serving size for a food record."""
    if food.serving_size_g:
        return f"{int(food.serving_size_g)} g"
    return "1 serving"


def _prefix(name: str) -> str:
    return (name or "").strip().lower().split(" ")[0]


def _energy_distance(food: FoodItem, per_item_target: float) -> float:
    return abs((food.energy_kcal or 0.0) - per_item_target)


def _select_for_slot(
    specific: list[FoodItem],
    generic: list[FoodItem],
    slot_budget: float,
    per_item_target: float,
    min_items: int,
    max_items: int,
    used_names: set[str],
) -> tuple[list[FoodItem], int]:
    """Pick the foods of a slot.

    ``specific`` holds foods that belong to this meal, ``generic`` holds foods
    that can be eaten at any time.  Generic foods are only used to top up a
    slot that would otherwise be too small.  ``used_names`` holds the foods
    that are already part of the day, so the same dish is never served twice.

    Returns the selected foods and the number of records that were skipped
    because they had no usable energy value.
    """
    def usable(foods: list[FoodItem]) -> list[FoodItem]:
        return [
            f
            for f in foods
            if (f.energy_kcal or 0) >= MIN_USABLE_ENERGY_KCAL
            and (f.name or "").strip().lower() not in used_names
        ]

    specific_usable = usable(specific)
    generic_usable = usable(generic)
    skipped = (len(specific) - len(specific_usable)) + (
        len(generic) - len(generic_usable)
    )

    ordered_specific = sorted(specific_usable, key=lambda f: _energy_distance(f, per_item_target))
    ordered_generic = sorted(generic_usable, key=lambda f: _energy_distance(f, per_item_target))

    selected: list[FoodItem] = []
    prefix_counts: dict[str, int] = {}
    accumulated = 0.0

    def take(food: FoodItem) -> None:
        nonlocal accumulated
        selected.append(food)
        used_names.add((food.name or "").strip().lower())
        prefix = _prefix(food.name)
        prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
        accumulated += food.energy_kcal or 0.0

    # 1. Fill the slot with foods that belong to it.
    for food in ordered_specific:
        if len(selected) >= max_items:
            break
        if selected and prefix_counts.get(_prefix(food.name), 0) >= 2:
            # Avoid filling a whole meal with the same kind of dish.
            continue
        energy = food.energy_kcal or 0.0
        if len(selected) >= min_items and accumulated + energy > slot_budget * SLOT_OVERSHOOT_TOLERANCE:
            # Adding this item would overshoot the slot budget noticeably.
            continue
        take(food)
        if len(selected) >= min_items and accumulated >= slot_budget:
            break

    # 2. Top up with foods that are not meal specific, but only when the slot
    #    would otherwise be too small.
    if len(selected) < min_items:
        for food in ordered_generic:
            if len(selected) >= min_items:
                break
            if selected and prefix_counts.get(_prefix(food.name), 0) >= 2:
                continue
            take(food)

    return selected, skipped


def build_meal_plan(
    foods: list[FoodItem], targets: NutrientTargets
) -> tuple[list[MealPlan], list[str]]:
    """Build the daily meal plan.

    Returns the meal slots with their items and totals plus a list of notes
    describing anything that had to be adjusted along the way.
    """
    notes: list[str] = []
    if not foods:
        return [], ["No foods are available to build a plan from."]

    recommender = KNNRecommender(n_neighbors=min(16, len(foods)))
    recommender.fit(foods)

    plans: list[MealPlan] = []
    used_names: set[str] = set()
    skipped_records = 0

    for slot in MEAL_SLOTS:
        share = SLOT_SHARES[slot]
        min_items, max_items = SLOT_ITEM_COUNTS[slot]
        slot_targets = scale_targets(targets, share)
        slot_budget = slot_targets.calories

        specific: list[FoodItem] = []
        generic: list[FoodItem] = []
        for food in foods:
            slots = specific_slots(food)
            if slot in slots:
                specific.append(food)
            elif not slots:
                # No meal marker at all - usable at any time of the day.
                generic.append(food)

        if not specific and not generic:
            notes.append(
                f"No {slot.lower()} food matched, so the remaining foods were used."
            )
            specific = list(foods)

        # Rank the candidates by how closely their nutrient profile matches a
        # single item of this meal, then let the energy fit decide.
        item_count = max(min_items, min(max_items, 4))
        per_item_targets = scale_targets(targets, share / item_count)
        pool_size = min(max(POOL_SIZE, item_count * 6), len(specific) or len(generic) or 1)
        ranked_specific = recommender.rank(
            specific, per_item_targets, top_k=pool_size
        ) if specific else []
        ranked_generic = recommender.rank(
            generic, per_item_targets, top_k=pool_size
        ) if generic else []

        selected, skipped = _select_for_slot(
            ranked_specific,
            ranked_generic,
            slot_budget=slot_budget,
            per_item_target=per_item_targets.calories,
            min_items=min_items,
            max_items=max_items,
            used_names=used_names,
        )
        if skipped:
            skipped_records += skipped
        if not selected:
            continue

        items = [
            MealItem(
                food_name=food.name,
                serving_size=serving_label(food),
                calories=round(food.energy_kcal or 0.0, 1),
                protein_g=round(food.protein_g or 0.0, 1),
                carbs_g=round(food.carbs_g or 0.0, 1),
                fat_g=round(food.fat_g or 0.0, 1),
            )
            for food in selected
        ]
        plans.append(
            MealPlan(
                meal=slot,
                items=items,
                totals=MealTotals(
                    calories=round(sum(item.calories for item in items), 1),
                    protein_g=round(sum(item.protein_g for item in items), 1),
                    carbs_g=round(sum(item.carbs_g for item in items), 1),
                    fat_g=round(sum(item.fat_g for item in items), 1),
                ),
            )
        )

    if skipped_records:
        notes.append(
            f"{skipped_records} food record(s) without a usable energy value were skipped."
        )

    return plans, notes
