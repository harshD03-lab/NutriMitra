"""Import the ICMR-NIN / IFCT nutrition dataset into the database.

The dataset ships with the server package so that a fresh deployment (for
example on Vercel) can initialise itself without relying on a developer
machine.  Two food files are used:

``Indian_Food_Nutrition_Processed.csv``
    IFCT 2017 processed composition data - 1,014 foods, values per 100 g of
    raw edible portion.  This is the primary source.

``input.csv``
    ICMR-NIN style list - 89 foods with per-100 g values plus the dataset's
    own meal and vegetarian markers.

``Indian_Food_Ingredients_Nutrition_CookingMethods.csv``
    Recipes with ingredients and instructions.  Recipes are optional: if the
    file is missing the food import still succeeds.

All paths are resolved relative to the installed package (or the
``DATA_DIR`` environment variable) - never hard coded to a developer machine.
"""

import csv
import os
import sys
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.food_item import FoodItem
from app.models.recipe import Recipe

CSV_FOOD_PRIMARY = "Indian_Food_Nutrition_Processed.csv"
CSV_FOOD_SUPPLEMENT = "input.csv"
CSV_RECIPES = "Indian_Food_Ingredients_Nutrition_CookingMethods.csv"

# Serving size the nutrient values are expressed in (per 100 g of raw edible
# portion for both source files).
DEFAULT_SERVING_SIZE_G = 100


class DatasetError(RuntimeError):
    """Raised when the nutrition dataset is missing or cannot be parsed."""


def candidate_data_dirs() -> list[Path]:
    """Directories that are searched for the dataset files."""
    server_dir = Path(__file__).resolve().parents[2]  # app/data -> server
    dirs = [
        Path(settings.DATA_DIR) if settings.DATA_DIR else None,
        server_dir / "data",
        server_dir,
        server_dir.parent,
        server_dir.parent / "data",
    ]
    seen: set[str] = set()
    ordered: list[Path] = []
    for directory in dirs:
        if directory is None:
            continue
        resolved = str(directory)
        if resolved in seen:
            continue
        seen.add(resolved)
        ordered.append(directory)
    return ordered


def find_dataset(filename: str) -> Path | None:
    """Return the path of a dataset file, or None when it is not present."""
    for directory in candidate_data_dirs():
        candidate = directory / filename
        if candidate.is_file():
            return candidate
    return None


def _clean_float(value) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", "").replace("–", "-").replace("−", "-")
    if not text:
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return number


def _pick(row: dict, *prefixes: str) -> float | None:
    """Read the first column whose name starts with one of *prefixes*."""
    for prefix in prefixes:
        for key, value in row.items():
            if key is None:
                continue
            if key.strip().lower().startswith(prefix.lower()):
                return _clean_float(value)
    return None


def _lookup(row: dict, *names: str) -> str:
    """Read the first column matching one of *names* (case insensitive)."""
    lowered = {str(k).strip().lower(): v for k, v in row.items() if k is not None}
    for name in names:
        if name in lowered:
            return (lowered[name] or "").strip()
    return ""


def _parse_veg_flag(raw: str) -> bool | None:
    """Parse the ICMR-NIN ``VegNovVeg`` marker.

    In the source file the column is set to ``1`` for the animal based dishes
    and ``0`` for everything else, so ``1`` means *non-vegetarian*.  (The
    previous implementation read it the other way round, which marked chicken
    and fish as vegetarian.)  A blank value means "unknown".
    """
    value = (raw or "").strip().lower()
    if value == "1":
        return False
    if value == "0":
        return True
    return None


def _parse_meal_flag(raw: str) -> bool:
    return (raw or "").strip() == "1"


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise DatasetError(f"{path.name} has no header row")
        return list(reader)


def _food_from_primary(row: dict) -> FoodItem | None:
    name = _lookup(row, "dish name", "food_items", "name")
    if not name:
        return None
    return FoodItem(
        name=name,
        category=_lookup(row, "category", "food group") or None,
        energy_kcal=_pick(row, "calories"),
        protein_g=_pick(row, "protein"),
        carbs_g=_pick(row, "carbohydrates"),
        fat_g=_pick(row, "fats", "fat"),
        sugar_g=_pick(row, "free sugar", "sugar", "sugars"),
        sodium_mg=_pick(row, "sodium"),
        fiber_g=_pick(row, "fibre", "fiber"),
        calcium_mg=_pick(row, "calcium"),
        iron_mg=_pick(row, "iron"),
        vitamin_c_mg=_pick(row, "vitamin c"),
        vitamin_a_mcg=_pick(row, "vitamin a"),
        folate_mcg=_pick(row, "folate"),
        zinc_mg=_pick(row, "zinc"),
        serving_size_g=DEFAULT_SERVING_SIZE_G,
        meal_type=None,
        is_veg=None,
    )


def _food_from_supplement(row: dict) -> FoodItem | None:
    name = _lookup(row, "food_items", "dish name", "name")
    if not name:
        return None
    breakfast = _parse_meal_flag(_lookup(row, "breakfast"))
    lunch = _parse_meal_flag(_lookup(row, "lunch"))
    dinner = _parse_meal_flag(_lookup(row, "dinner"))
    if breakfast:
        meal_type = "breakfast"
    elif lunch:
        meal_type = "lunch"
    elif dinner:
        meal_type = "dinner"
    else:
        meal_type = None
    return FoodItem(
        name=name,
        category=_lookup(row, "category", "food group") or None,
        energy_kcal=_pick(row, "calories"),
        protein_g=_pick(row, "proteins", "protein"),
        carbs_g=_pick(row, "carbohydrates", "carbs"),
        fat_g=_pick(row, "fats", "fat"),
        sugar_g=_pick(row, "sugars", "sugar", "free sugar"),
        sodium_mg=_pick(row, "sodium"),
        fiber_g=_pick(row, "fibre", "fiber"),
        calcium_mg=_pick(row, "calcium"),
        iron_mg=_pick(row, "iron"),
        vitamin_c_mg=_pick(row, "vitamin c"),
        vitamin_a_mcg=_pick(row, "vitamin a"),
        folate_mcg=_pick(row, "folate"),
        zinc_mg=_pick(row, "zinc"),
        serving_size_g=DEFAULT_SERVING_SIZE_G,
        meal_type=meal_type,
        is_veg=_parse_veg_flag(_lookup(row, "vegnovveg", "veg")),
    )


def _merge_missing(target: FoodItem, source: FoodItem) -> None:
    """Copy values that are missing on *target* from *source*."""
    for field in (
        "category", "energy_kcal", "protein_g", "carbs_g", "fat_g", "sugar_g",
        "sodium_mg", "fiber_g", "calcium_mg", "iron_mg", "vitamin_c_mg",
        "vitamin_a_mcg", "folate_mcg", "zinc_mg",
    ):
        if getattr(target, field) in (None, "") and getattr(source, field) not in (None, ""):
            setattr(target, field, getattr(source, field))
    if target.meal_type is None and source.meal_type is not None:
        target.meal_type = source.meal_type
    if target.is_veg is None and source.is_veg is not None:
        target.is_veg = source.is_veg


def _key(name: str) -> str:
    return " ".join(name.strip().lower().split())


def _import_foods(db: Session, path: Path, builder) -> int:
    rows = _read_csv(path)
    if not rows:
        raise DatasetError(f"{path.name} does not contain any data rows")
    imported = 0
    for row in rows:
        item = builder(row)
        if item is None or not item.name:
            continue
        db.add(item)
        imported += 1
    return imported


def _deduplicate_foods(db: Session) -> int:
    """Collapse duplicate food names, keeping the most complete record."""
    items = db.query(FoodItem).all()
    by_name: dict[str, FoodItem] = {}
    duplicates = 0
    for item in items:
        key = _key(item.name)
        if key not in by_name:
            by_name[key] = item
            continue
        keeper = by_name[key]
        _merge_missing(keeper, item)
        db.delete(item)
        duplicates += 1
    db.commit()
    return duplicates


def _import_recipes(db: Session, path: Path) -> int:
    rows = _read_csv(path)
    count = 0
    for row in rows:
        name = _lookup(row, "final_food_name", "recipe_original", "name")
        if not name:
            continue
        food = db.query(FoodItem).filter(FoodItem.name == name).first()
        db.add(
            Recipe(
                food_id=food.id if food else None,
                cuisine=_lookup(row, "cuisine") or None,
                cooking_time_mins=int(_clean_float(_lookup(row, "totaltimeinmins", "total time")) or 0) or None,
                ingredients=_lookup(row, "translatedingredients", "ingredients") or None,
                instructions=_lookup(row, "translatedinstructions", "instructions") or None,
            )
        )
        count += 1
        if count % 200 == 0:
            db.commit()
    db.commit()
    return count


def load_food_dataset(db: Session, include_recipes: bool = True) -> dict:
    """Import the food dataset (and optionally the recipes) into the database.

    Raises :class:`DatasetError` when the dataset is missing or unusable so
    that the caller can report a real error instead of an empty plan.
    """
    primary = find_dataset(CSV_FOOD_PRIMARY)
    supplement = find_dataset(CSV_FOOD_SUPPLEMENT)
    if primary is None and supplement is None:
        searched = ", ".join(str(d) for d in candidate_data_dirs())
        raise DatasetError(
            "Nutrition dataset not found. Expected "
            f"'{CSV_FOOD_PRIMARY}' or '{CSV_FOOD_SUPPLEMENT}' in one of: {searched}. "
            "Set DATA_DIR to the folder that contains the dataset files."
        )

    food_count = 0
    if primary is not None:
        food_count += _import_foods(db, primary, _food_from_primary)
    if supplement is not None:
        food_count += _import_foods(db, supplement, _food_from_supplement)
    db.commit()

    if food_count == 0:
        raise DatasetError(
            "The nutrition dataset was found but no usable food records could be parsed."
        )

    duplicates = _deduplicate_foods(db)
    food_count = db.query(FoodItem).count()

    recipe_count = 0
    recipes_path = find_dataset(CSV_RECIPES)
    if include_recipes and recipes_path is not None:
        if db.query(Recipe).count() == 0:
            try:
                recipe_count = _import_recipes(db, recipes_path)
            except Exception as exc:  # recipes are optional - never fail the food import
                db.rollback()
                recipe_count = 0
                print(f"Warning: recipe import failed ({exc}); foods were still imported")

    return {
        "foods": food_count,
        "recipes": recipe_count,
        "duplicates_removed": duplicates,
        "sources": [
            str(p) for p in (primary, supplement) if p is not None
        ],
    }


def main() -> int:
    """Manual import entry point: ``python -m app.data.seed_foods``."""
    from app.core.database import Base, SessionLocal, engine

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        result = load_food_dataset(db)
    except DatasetError as exc:
        print(f"ERROR: {exc}")
        return 1
    finally:
        db.close()
    print(
        f"Imported {result['foods']} foods "
        f"({result['duplicates_removed']} duplicates removed) and "
        f"{result['recipes']} recipes from: {', '.join(result['sources'])}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
