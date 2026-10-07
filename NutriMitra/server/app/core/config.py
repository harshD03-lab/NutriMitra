import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "NutriMitra API"
    DATABASE_URL: str = os.getenv("DATABASE_URL") or (
        "sqlite:////tmp/nutrimitra.db" if os.getenv("VERCEL") else "./nutrimitra.db"
    )
    SECRET_KEY: str = os.getenv("SECRET_KEY", "thisisasecretkey123456789012")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"


settings = Settings()
