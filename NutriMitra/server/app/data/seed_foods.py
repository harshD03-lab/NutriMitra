import csv
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.food_item import FoodItem
from app.models.recipe import Recipe

COLUMN_ALIASES = {
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
    "breakfast_flag": [
        "breakfast",
    ],
    "lunch_flag": [
        "lunch",
    ],
    "dinner_flag": [
        "dinner",
    ],
    "is_veg": [
        "veg", "vegetarian", "non veg", "nonvegetarian", "vegnoveg", "is_veg"
    ],
}

# Recipe CSV column aliases
RECIPE_COLUMN_ALIASES = {
    "final_food_name": [
        "recipe_original", "final_food_name", "name", "food_name", "dish", "recipe_name"
    ],
    "cuisine": ["cuisine", "region", "cuisine type"],
    "cooking_time_mins": ["totaltimeinmins", "time", "cooking time", "cooking_time", "total time"],
    "ingredients": ["translatedingredients", "ingredients", "recipe_ingredients"],
    "instructions": ["translatedinstructions", "instructions", "recipe_instructions"],
    "calories_kcal": ["calories (kcal)", "calories", "calorie"],
    "protein_g": ["protein (g)", "protein", "protein_g"],
    "carbs_g": ["carbohydrates (g)", "carbs", "carbohydrates", "carbs_g"],
    "fats_g": ["fats (g)", "fats", "fat", "fat_g"],
    "fiber_g": ["fibre (g)", "fiber", "fiber_g"],
    "sodium_mg": ["sodium (mg)", "sodium", "sodium_mg"],
    "calcium_mg": ["calcium (mg)", "calcium", "calcium_mg"],
    "iron_mg": ["iron (mg)", "iron", "iron_mg"],
    "vitamin_c_mg": ["vitamin c (mg)", "vitamin_c", "vitamin c", "vitamin_c_mg"],
    "folate_mcg": ["folate (µg)", "folate", "folate_mcg", "folic acid"],
}


def _normalise(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def _build_col_map(headers: list[str], column_aliases: dict[str, list[str]]) -> dict[str, str]:
    col_map: dict[str, str] = {}
    for raw in headers:
        n = _normalise(raw)
        for field, aliases in column_aliases.items():
            if any(n == _normalise(a) or n.startswith(_normalise(a)) for a in aliases):
                col_map[raw] = field
                break
    return col_map


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


def _parse_veg_status(veg_str: str | None) -> bool | None:
    if not veg_str:
        return None
    veg_str = veg_str.strip().lower()
    # Handle numeric values from CSV (0 or 1)
    if veg_str in ['0', '1']:
        return veg_str == '1'  # 1 = True (veg), 0 = False (non-veg)
    # Handle text values
    if veg_str in ["veg", "vegetarian", "v", "yes", "true"]:
        return True
    elif veg_str in ["non veg", "nonvegetarian", "nv", "no", "false"]:
        return False
    # Special case for space (from the CSV) - treat as unknown
    elif veg_str == ' ':
        return None
    return None


def _parse_meal_type(meal_str: str | None) -> str | None:
    if not meal_str:
        return None
    meal_str = meal_str.strip().lower()
    # Handle numeric values from CSV (0 or 1 flags)
    if meal_str in ['0', '1']:
        # This will be interpreted by the caller based on which column it came from
        # We'll return the raw value and let the calling code map it to meal type
        return meal_str
    # Handle text values
    meal_mapping = {
        "breakfast": "breakfast",
        "lunch": "lunch", 
        "dinner": "dinner",
        "snack": "snack",
        "snacks": "snack",
        "appetizer": "appetizer",
    }
    return meal_mapping.get(meal_str, None)


def load_icmr_data(csv_path: str, db_path: str = r'C:\Users\harsh\OneDrive\Documents\ALL Projext\Open code\Diet System\NutriMitra\server\nutrimitra.db') -> tuple[int, int]:
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    db = SessionLocal()
    
    count = 0
    recipe_count = 0
    
    try:
        # Load food items
        with open(csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                print("No headers found in CSV")
                return 0, 0
            col_map = _build_col_map(reader.fieldnames, COLUMN_ALIASES)
            missing = set(COLUMN_ALIASES.keys()) - set(col_map.values())
            if "name" not in col_map.values():
                print("ERROR: no 'name' column found in CSV headers")
                print(f"  Headers: {reader.fieldnames}")
                return 0, 0
            if missing:
                print(f"Note: missing columns -> {', '.join(sorted(missing))}")

            for row in reader:
                mapped: dict[str, str] = {}
                for csv_col, model_col in col_map.items():
                    mapped[model_col] = row.get(csv_col, "").strip()
                
                # Parse special fields
                veg_status = _parse_veg_status(mapped.get("is_veg"))
                
                # Parse meal type from the individual flags (Breakfast, Lunch, Dinner columns)
                meal_type = None
                breakfast_val = mapped.get("breakfast_flag")
                lunch_val = mapped.get("lunch_flag")
                dinner_val = mapped.get("dinner_flag")
                
                # Check which meal type flags are set to "1" (priority: breakfast > lunch > dinner)
                if breakfast_val == "1":
                    meal_type = "breakfast"
                elif lunch_val == "1":
                    meal_type = "lunch"
                elif dinner_val == "1":
                    meal_type = "dinner"
                # If none are set to "1", meal_type remains None
                
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
                    meal_type=meal_type,
                    is_veg=veg_status,
                )
                db.add(item)
                count += 1
                if count % 100 == 0:
                    db.commit()
        
        db.commit()
        
        # Load recipe data
        recipe_csv_path = r"C:\Users\harsh\OneDrive\Documents\ALL Projext\Open code\Diet System\Indian_Food_Ingredients_Nutrition_CookingMethods.csv"
        with open(recipe_csv_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                col_map = _build_col_map(reader.fieldnames, RECIPE_COLUMN_ALIASES)
                
                for row in reader:
                    mapped: dict[str, str] = {}
                    for csv_col, model_col in col_map.items():
                        mapped[model_col] = row.get(csv_col, "").strip()
                    
                    # Find or create food item
                    food_name = mapped.get("final_food_name")
                    if not food_name:
                        continue
                        
                    food_item = db.query(FoodItem).filter(FoodItem.name.ilike(food_name)).first()
                    
                    recipe = Recipe(
                        food_id=food_item.id if food_item else None,
                        cuisine=mapped.get("cuisine"),
                        cooking_time_mins=_int_or_none(mapped.get("cooking_time_mins")),
                        ingredients=mapped.get("ingredients"),
                        instructions=mapped.get("instructions"),
                    )
                    db.add(recipe)
                    recipe_count += 1
                    if recipe_count % 50 == 0:
                        db.commit()
        
        db.commit()
        print(f"Loaded {count} food items and {recipe_count} recipes")
        return count, recipe_count
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        return 0, 0
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    import os

    # Default paths - use the files in the Diet System folder
    food_csv = r"C:\Users\harsh\OneDrive\Documents\ALL Projext\Open code\Diet System\input.csv"
    recipe_csv = r"C:\Users\harsh\OneDrive\Documents\ALL Projext\Open code\Diet System\Indian_Food_Ingredients_Nutrition_CookingMethods.csv"
    db_path = r"C:\Users\harsh\OneDrive\Documents\ALL Projext\Open code\Diet System\NutriMitra\server\nutrimitra.db"
    
    # Use provided path or default
    path = sys.argv[1] if len(sys.argv) > 1 else food_csv
    
    # Check if CSV files exist
    if not os.path.exists(path):
        print(f"Error: Food CSV file not found at {path}")
        sys.exit(1)
    
    if not os.path.exists(recipe_csv):
        print(f"Warning: Recipe CSV file not found at {recipe_csv}")
        # Don't exit, just continue without recipes
    
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        sys.exit(1)
    
    # Run the seeding process
    food_count, recipe_count = load_icmr_data(path, db_path)
    print(f"Loaded {food_count} food items and {recipe_count} recipes from {path}")
    
    # Show results
    import sqlite3
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM food_items")
    total_foods = c.fetchone()[0]
    print(f"Total food items in database: {total_foods}")
    
    c.execute("SELECT COUNT(*) FROM recipes")
    total_recipes = c.fetchone()[0]
    print(f"Total recipes in database: {total_recipes}")
    
    c.execute("SELECT name, meal_type, is_veg FROM food_items WHERE meal_type IS NOT NULL OR is_veg IS NOT NULL ORDER BY name LIMIT 10")
    sample_data = c.fetchall()
    print(f"\nSample new data (meal_type, is_veg):")
    for row in sample_data:
        print(f"  {row[0]}: meal_type={row[1]}, is_veg={row[2]}")
    
    conn.close()
