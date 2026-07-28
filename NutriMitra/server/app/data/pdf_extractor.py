"""
Extract Indian food composition tables from PDF (ICMR-NIN format)
using pdfplumber and load them into the database.
"""

import csv
import re
from pathlib import Path

import pdfplumber

from app.core.database import SessionLocal
from app.models.food_item import FoodItem

COLUMN_ALIASES: dict[str, str] = {
    "name": ["name", "food", "food name", "food item", "item", "description"],
    "category": ["category", "group", "food group", "type", "class"],
    "energy_kcal": [
        "energy", "energy_kcal", "kcal", "calories", "energy (kcal)", "energy kcal",
    ],
    "protein_g": [
        "protein", "protein_g", "protein (g)", "protein g",
    ],
    "carbs_g": [
        "carbs", "carbohydrates", "carbs_g", "carbohydrates (g)", "carbs (g)",
        "cho", "cho (g)",
    ],
    "fat_g": [
        "fat", "fat_g", "fat (g)", "total fat", "total fat (g)",
    ],
    "fiber_g": [
        "fiber", "fibre", "fiber_g", "dietary fiber", "dietary fibre",
        "fiber (g)", "fibre (g)", "crude fiber", "crude fibre",
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
        "retinol", "retinol (mcg)", "beta-carotene",
    ],
    "folate_mcg": [
        "folate", "folate_mcg", "folate (mcg)", "folic acid",
        "folic acid (mcg)", "vitamin b9",
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


def _match_column(raw: str) -> str | None:
    n = _normalise(raw)
    for field, aliases in COLUMN_ALIASES.items():
        if any(n == _normalise(a) or n.startswith(_normalise(a)) for a in aliases):
            return field
    return None


def extract_tables(pdf_path: str) -> list[dict]:
    rows: list[dict] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 2:
                    continue
                header = [_normalise(c) if c else "" for c in table[0]]
                col_map: dict[int, str] = {}
                for i, h in enumerate(header):
                    mapped = _match_column(h)
                    if mapped:
                        col_map[i] = mapped
                if "name" not in col_map.values():
                    continue
                for row in table[1:]:
                    if not any(cell and cell.strip() for cell in row):
                        continue
                    record: dict[str, str] = {}
                    for i, cell in enumerate(row):
                        field = col_map.get(i)
                        if field and cell:
                            record[field] = cell.strip()
                    if "name" in record:
                        rows.append(record)
    return rows


def records_to_csv(records: list[dict], csv_path: str):
    fieldnames = [f.name for f in FoodItem.__table__.columns if f.name != "id"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for rec in records:
            row = {k: rec.get(k, "") for k in fieldnames}
            writer.writerow(row)
    print(f"Wrote {len(records)} rows to {csv_path}")


def _float(val: str | None) -> float | None:
    if not val:
        return None
    cleaned = re.sub(r"[^\d.]", "", val.replace(",", ""))
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


def records_to_db(records: list[dict]):
    db = SessionLocal()
    count = 0
    try:
        for rec in records:
            item = FoodItem(
                name=rec.get("name", "").strip(),
                category=rec.get("category", "").strip(),
                energy_kcal=_float(rec.get("energy_kcal")),
                protein_g=_float(rec.get("protein_g")),
                carbs_g=_float(rec.get("carbs_g")),
                fat_g=_float(rec.get("fat_g")),
                fiber_g=_float(rec.get("fiber_g")),
                calcium_mg=_float(rec.get("calcium_mg")),
                iron_mg=_float(rec.get("iron_mg")),
                vitamin_c_mg=_float(rec.get("vitamin_c_mg")),
                vitamin_a_mcg=_float(rec.get("vitamin_a_mcg")),
                folate_mcg=_float(rec.get("folate_mcg")),
                zinc_mg=_float(rec.get("zinc_mg")),
                serving_size_g=_float(rec.get("serving_size_g")),
                suitable_for=rec.get("suitable_for", "").strip(),
            )
            db.add(item)
            count += 1
            if count % 50 == 0:
                db.commit()
        db.commit()
    finally:
        db.close()
    return count


if __name__ == "__main__":
    import sys

    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "data/raw/indian_food.pdf"
    out_csv = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"Extracting tables from {pdf_path} ...")
    records = extract_tables(pdf_path)
    print(f"Found {len(records)} food records")

    if out_csv:
        records_to_csv(records, out_csv)
    else:
        n = records_to_db(records)
        print(f"Inserted {n} food items into the database")
