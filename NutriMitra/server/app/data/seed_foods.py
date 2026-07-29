"""
ICMR-NIN / Indian Food Nutrition CSV processing script.

Reads a food composition CSV (supports multiple column naming formats)
and inserts rows into the food_items table via SQLAlchemy.
"""

import csv
import re

from app.core.database import SessionLocal
from app.models.food_item import FoodItem

COLUMN_ALIASES: dict[str, list[str]] = {
    "name": [
        "name", "dish name", "food", "food name", "food item", "item", "description",
    ],
    "category": ["category", "group", "food group", "type", "class"],
    "energy_kcal": [
        "energy", "energy_kcal", "kcal", "calories", "energy (kcal)", "calories (kcal)",
    ],
    "protein_g": [
        "protein", "protein_g", "protein (g)",
    ],
    "carbs_g": [
        "carbs", "carbohydrates", "carbs_g", "carbohydrates (g)", "carbs (g)",
        "cho", "cho (g)",
    ],
    "fat_g": [
        "fat", "fats", "fat_g", "fats (g)", "fat (g)", "total fat", "total fat (g)",
    ],
    "fiber_g": [
        "fiber", "fibre", "fiber_g", "fibre (g)", "fiber (g)", "dietary fiber",
        "dietary fibre",
    ],
    "calcium_mg": [
        "calcium", "calcium_mg", "calcium (mg)", "ca", "ca (mg)",
    ],
    "iron_mg": [
        "iron", "iron_mg", "iron (mg)", "fe", "fe (mg)",
    ],
    "vitamin_c_mg": [
        "vitamin c", "vitamin_c", "vitamin_c_mg", "vitamin c (mg)",
        "ascorbic acid", "ascorbic acid (mg)",
    ],
    "vitamin_a_mcg": [
        "vitamin a", "vitamin_a", "vitamin_a_mcg", "vitamin a (mcg)",
        "retinol", "retinol (mcg)",
    ],
    "folate_mcg": [
        "folate", "folate_mcg", "folate (mcg)", "folate (µg)",
        "folic acid", "folic acid (mcg)",
    ],
    "zinc_mg": [
        "zinc", "zinc_mg", "zinc (mg)", "zn", "zn (mg)",
    ],
    "serving_size_g": [
        "serving size", "serving_size", "serving_size_g", "portion",
        "serving size (g)", "weight (g)", "per serving (g)",
    ],
    "suitable_for": [
        "suitable for", "suitable_for", "restrictions", "notes", "remarks",
    ],
}


def _normalise(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def _build_col_map(headers: list[str]) -> dict[str, str]:
    col_map: dict[str, str] = {}
    for raw in headers:
        n = _normalise(raw)
        for field, aliases in COLUMN_ALIASES.items():
            if any(n == _normalise(a) or n.startswith(_normalise(a)) for a in aliases):
                col_map[raw] = field
                break
    return col_map


def load_icmr_data(csv_path: str) -> int:
    db = SessionLocal()
    count = 0
    try:
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                print("No headers found in CSV")
                return 0
            col_map = _build_col_map(reader.fieldnames)
            missing = set(COLUMN_ALIASES.keys()) - set(col_map.values())
            if "name" not in col_map.values():
                print("ERROR: no 'name' column found in CSV headers")
                print(f"  Headers: {reader.fieldnames}")
                return 0
            if missing:
                print(f"Note: missing columns → {', '.join(sorted(missing))}")

            for row in reader:
                mapped: dict[str, str] = {}
                for csv_col, model_col in col_map.items():
                    mapped[model_col] = row.get(csv_col, "").strip()
                item = FoodItem(
                    name=mapped.get("name", ""),
                    category=mapped.get("category", ""),
                    energy_kcal=_float(mapped.get("energy_kcal")),
                    protein_g=_float(mapped.get("protein_g")),
                    carbs_g=_float(mapped.get("carbs_g")),
                    fat_g=_float(mapped.get("fat_g")),
                    fiber_g=_float(mapped.get("fiber_g")),
                    calcium_mg=_float(mapped.get("calcium_mg")),
                    iron_mg=_float(mapped.get("iron_mg")),
                    vitamin_c_mg=_float(mapped.get("vitamin_c_mg")),
                    vitamin_a_mcg=_float(mapped.get("vitamin_a_mcg")),
                    folate_mcg=_float(mapped.get("folate_mcg")),
                    zinc_mg=_float(mapped.get("zinc_mg")),
                    serving_size_g=_int_or_none(mapped.get("serving_size_g")),
                    suitable_for=mapped.get("suitable_for", ""),
                )
                db.add(item)
                count += 1
                if count % 100 == 0:
                    db.commit()
            db.commit()
    finally:
        db.close()
    return count


def _float(val: str | None) -> float | None:
    if not val:
        return None
    cleaned = re.sub(r"[^\d.−–-]", "", val.replace(",", "").replace("−", "-").replace("–", "-"))
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def _int_or_none(val: str | None) -> int | None:
    if not val:
        return None
    cleaned = re.sub(r"[^\d.−–-]", "", val.replace(",", "").replace("−", "-").replace("–", "-"))
    try:
        return int(float(cleaned)) if cleaned else None
    except ValueError:
        return None


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "data/raw/indian_food.csv"
    n = load_icmr_data(path)
    print(f"Loaded {n} food items from {path}")
