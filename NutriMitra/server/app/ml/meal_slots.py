"""Meal slot inference.

The dataset carries a ``meal_type`` column for a small part of the data and
dish names for the rest.  The category column is empty for most rows, so
slot eligibility is derived from the stored marker first and from the dish
name second.
"""

import re

from app.ml.diet_rules import tokenize
from app.models.food_item import FoodItem

BREAKFAST = "Breakfast"
LUNCH = "Lunch"
DINNER = "Dinner"
SNACKS = "Snacks"

MEAL_SLOTS = [BREAKFAST, LUNCH, DINNER, SNACKS]

# Share of the daily energy target that each slot is planned for.
SLOT_SHARES: dict[str, float] = {
    BREAKFAST: 0.25,
    LUNCH: 0.30,
    DINNER: 0.30,
    SNACKS: 0.15,
}

# How many foods are planned per slot (minimum and maximum).
SLOT_ITEM_COUNTS: dict[str, tuple[int, int]] = {
    BREAKFAST: (3, 5),
    LUNCH: (3, 5),
    DINNER: (3, 5),
    SNACKS: (1, 3),
}

SLOT_KEYWORDS: dict[str, set[str]] = {
    BREAKFAST: {
        "milk", "tea", "coffee", "juice", "bread", "toast", "idli", "upma",
        "poha", "dosa", "chutney", "oats", "porridge", "halwa", "ragi",
        "suji", "daliya", "vermicelli", "sheera", "appam", "eggs", "egg",
        "omelette", "omlet", "cereal", "cornflakes", "muesli", "buttermilk",
        "lassi", "curd", "yogurt",
    },
    LUNCH: {
        "dal", "daal", "rice", "roti", "chapati", "paratha", "curry", "sabzi",
        "vegetable", "vegetables", "biryani", "pulao", "khichdi", "kofta",
        "sambar", "chole", "rajma", "pasta", "noodles", "sandwich", "burger",
        "pizza", "soup", "chawal", "tandoori", "tikka", "batter", "roll",
        "chawal", "pulses", "lentil", "beans", "tofu", "soya", "soybean",
    },
    DINNER: {
        "soup", "salad", "roti", "chapati", "paratha", "dal", "daal", "rice",
        "khichdi", "sabzi", "curry", "dosa", "sandwich", "pasta", "noodles",
        "stir", "fry", "grill", "tandoori", "biryani", "pulao", "khichri",
    },
    SNACKS: {
        "biscuit", "biscuits", "chips", "namkeen", "pakora", "pakoda", "samosa",
        "fruit", "fruits", "chocolate", "cake", "candy", "popcorn", "peanut",
        "groundnut", "murmura", "chivda", "thepla", "mathri", "laddu",
        "jalebi", "kulfi", "ice", "icecream", "cream", "juice", "tea", "coffee",
        "nuts", "cashew", "almond", "walnut", "pistachio", "raisin", "mixture",
        "makhana", "trail", "barfi", "burfi", "jamun", "halwa", "ladoo",
    },
}

_SLOT_BY_MEAL_TYPE = {
    "breakfast": BREAKFAST,
    "lunch": LUNCH,
    "dinner": DINNER,
    "snack": SNACKS,
    "snacks": SNACKS,
    "appetizer": SNACKS,
}


def slot_from_meal_type(meal_type: str | None) -> str | None:
    if not meal_type:
        return None
    return _SLOT_BY_MEAL_TYPE.get(meal_type.strip().lower())


def specific_slots(food: FoodItem) -> set[str]:
    """Slots the dataset or the dish name points at explicitly."""
    slots: set[str] = set()

    stored = slot_from_meal_type(food.meal_type)
    if stored:
        slots.add(stored)

    tokens = tokenize(food.name)
    for slot, keywords in SLOT_KEYWORDS.items():
        if tokens & keywords:
            slots.add(slot)
    return slots


def infer_slots(food: FoodItem) -> set[str]:
    """Return every meal slot a food is suitable for."""
    slots = specific_slots(food)
    if not slots:
        # Generic single foods (a vegetable, a fruit, a pulse) can be eaten at
        # any meal - they are offered for lunch and dinner.
        slots.add(LUNCH)
        slots.add(DINNER)
    return slots
