import logging
import traceback
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from app.api.v1.api import router as v1_router
from app.core.config import settings
from app.core.database import Base, engine

logger = logging.getLogger("nutrimitra")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        
        # Seed the database with ICMR-NIN data if it's empty
        from app.data.seed_foods import load_icmr_data
        import os
        
        # Check if we have food data already
        from app.core.database import SessionLocal
        from app.models.food_item import FoodItem
        
        db = SessionLocal()
        try:
            food_count = db.query(FoodItem).count()
            if food_count == 0:
                print("No food data found, seeding ICMR-NIN dataset...")
                # Use absolute paths based on current file location for Vercel compatibility
                # Go up two levels: main.py -> app -> server
                current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                food_csv = os.path.join(current_dir, "input.csv")
                recipe_csv = os.path.join(current_dir, "Indian_Food_Ingredients_Nutrition_CookingMethods.csv")
                db_path = os.path.join(current_dir, "nutrimitra.db")
                
                print(f"Looking for food CSV at: {food_csv}")
                print(f"Looking for recipe CSV at: {recipe_csv}")
                print(f"Database path: {db_path}")
                
                # Check if CSV files exist
                if os.path.exists(food_csv) and os.path.exists(recipe_csv):
                    # Fix the database path for SQLAlchemy - needs sqlite:/// prefix
                    db_connection_string = f"sqlite:///{db_path}"
                    count, recipe_count = load_icmr_data(food_csv, db_connection_string)
                    print(f"Seeded {count} food items and {recipe_count} recipes")
                else:
                    if not os.path.exists(food_csv):
                        print(f"Warning: Food CSV not found at {food_csv}")
                    if not os.path.exists(recipe_csv):
                        print(f"Warning: Recipe CSV not found at {recipe_csv}")
            else:
                print(f"Database already contains {food_count} food items, skipping seed")
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error during startup: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(v1_router, prefix="/v1")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled error on %s %s\n%s",
        request.method,
        request.url.path,
        traceback.format_exc(),
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Server error while handling {request.url.path}: "
                      f"{type(exc).__name__}: {exc}. Check the server logs for details."
        },
    )

static_dir = Path(__file__).resolve().parent.parent / "static"
assets_dir = static_dir / "assets"
if static_dir.exists() and assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        if full_path.startswith("v1/"):
            # If it's an API path that wasn't found by the API router, return 404
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(static_dir / "index.html")
else:
    @app.get("/")
    async def root():
        return {"status": "API running", "frontend": "build not found – run `npm run build` in client/"}

    @app.exception_handler(404)
    async def not_found(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "Not found"}, status_code=404)
