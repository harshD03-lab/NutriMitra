"""
ICMR-NIN Indian food composition dataset processing script.

Reads the raw CSV from data/raw/indian_food.csv and inserts
rows into the food_items table via SQLAlchemy.
"""

import csv

from app.core.database import SessionLocal
from app.models.food_item import FoodItem


def load_icmr_data(csv_path: str) -> int:
    db = SessionLocal()
    count = 0
    try:
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                item = FoodItem(
                    name=row.get("name", "").strip(),
                    category=row.get("category", "").strip(),
                    energy_kcal=_float(row.get("energy_kcal")),
                    protein_g=_float(row.get("protein_g")),
                    carbs_g=_float(row.get("carbs_g")),
                    fat_g=_float(row.get("fat_g")),
                    fiber_g=_float(row.get("fiber_g")),
                    calcium_mg=_float(row.get("calcium_mg")),
                    iron_mg=_float(row.get("iron_mg")),
                    vitamin_c_mg=_float(row.get("vitamin_c_mg")),
                    vitamin_a_mcg=_float(row.get("vitamin_a_mcg")),
                    folate_mcg=_float(row.get("folate_mcg")),
                    zinc_mg=_float(row.get("zinc_mg")),
                    serving_size_g=_int_or_none(row.get("serving_size_g")),
                    suitable_for=row.get("suitable_for", "").strip(),
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
    if val is None or val.strip() == "":
        return None
    try:
        return float(val.strip())
    except ValueError:
        return None


def _int_or_none(val: str | None) -> int | None:
    if val is None or val.strip() == "":
        return None
    try:
        return int(float(val.strip()))
    except ValueError:
        return None


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "data/raw/indian_food.csv"
    n = load_icmr_data(path)
    print(f"Loaded {n} food items from {path}")
