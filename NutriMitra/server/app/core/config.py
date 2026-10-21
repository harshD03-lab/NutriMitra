import os
from pydantic_settings import BaseSettings


# Get the directory of this config file
CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up two levels to get the server directory: config.py -> app -> server
SERVER_DIR = os.path.dirname(os.path.dirname(CONFIG_DIR))


class Settings(BaseSettings):
    APP_NAME: str = "NutriMitra API"
    DATABASE_URL: str = (
        os.getenv("DATABASE_URL")
        or os.getenv("POSTGRES_URL")
        or "postgresql://nutrimitra:nutrimitra@localhost:5433/nutrimitra"
    )
    # Directory that holds the nutrition dataset.  Defaults to the folder that
    # ships with the server package so the dataset is available in the
    # deployed environment (and can be overridden with the DATA_DIR env var).
    DATA_DIR: str = os.getenv("DATA_DIR") or SERVER_DIR
    SECRET_KEY: str = os.getenv("SECRET_KEY", "thisisasecretkey123456789012")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    class Config:
        env_file = ".env"


settings = Settings()
