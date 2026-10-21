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
from app.core.database import Base, SessionLocal, engine, ensure_schema
from app.data.seed_foods import DatasetError, load_food_dataset
from app.models.food_item import FoodItem

logger = logging.getLogger("nutrimitra")
logging.basicConfig(level=logging.INFO)

# Runtime state of the nutrition dataset.  The API reports a clear error when
# the dataset could not be loaded instead of returning an empty meal plan.
DATASET_STATUS: dict = {"available": False, "foods": 0, "error": None}


def _seed_dataset_if_empty() -> None:
    """Populate the food table from the bundled dataset when it is empty."""
    db = SessionLocal()
    try:
        food_count = db.query(FoodItem).count()
        if food_count > 0:
            DATASET_STATUS.update(available=True, foods=food_count, error=None)
            logger.info("Nutrition dataset already present with %s foods", food_count)
            return
        logger.info("No food data found - importing the bundled nutrition dataset")
        result = load_food_dataset(db)
        DATASET_STATUS.update(
            available=True, foods=result["foods"], error=None
        )
        logger.info(
            "Imported %s foods and %s recipes from %s",
            result["foods"],
            result["recipes"],
            ", ".join(result["sources"]),
        )
    except DatasetError as exc:
        DATASET_STATUS.update(available=False, foods=0, error=str(exc))
        logger.error("Nutrition dataset unavailable: %s", exc)
    except Exception as exc:  # pragma: no cover - defensive
        db.rollback()
        DATASET_STATUS.update(
            available=False, foods=0, error=f"Dataset import failed: {exc}"
        )
        logger.error("Nutrition dataset import failed: %s", exc)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ready")
    except Exception:
        logger.error("Could not create database tables:\n%s", traceback.format_exc())
        raise

    try:
        applied = ensure_schema()
        if applied:
            logger.info("Applied column migrations: %s", ", ".join(applied))
    except Exception:
        logger.error("Could not apply column migrations:\n%s", traceback.format_exc())

    _seed_dataset_if_empty()
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
