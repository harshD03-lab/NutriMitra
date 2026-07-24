from fastapi import APIRouter

from app.api.v1.routes import auth, food, recommendations, users

router = APIRouter(prefix="/v1")
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(food.router)
router.include_router(recommendations.router)
