from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "NutriMitra API"
    DATABASE_URL: str = "sqlite:///./nutrimitra.db"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"


settings = Settings()
