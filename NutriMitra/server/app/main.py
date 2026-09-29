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
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(v1_router)


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
        if full_path.startswith("v1/") or full_path.startswith("assets/"):
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
