import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from urllib.parse import urlparse

from app.core.config import settings


def _get_engine():
    database_url = settings.DATABASE_URL
    
    # For SQLite URLs, ensure the directory exists
    if database_url.startswith("sqlite:///"):
        # Extract the file path from sqlite:///path/to/file.db
        # sqlite:/// -> 10 chars, but we need to handle both relative and absolute
        if database_url.startswith("sqlite:////"):
            # Absolute path: sqlite:////tmp/file.db -> /tmp/file.db
            file_path = database_url[10:]  # Remove sqlite://// prefix
        elif database_url.startswith("sqlite:///"):
            # Relative path: sqlite:///./file.db -> ./file.db
            file_path = database_url[9:]   # Remove sqlite:/// prefix
        else:
            # Fallback, shouldn't happen with valid SQLite URLs
            file_path = database_url[9:]
        
        # Ensure the directory exists
        if file_path:
            dir_name = os.path.dirname(file_path)
            if dir_name and not os.path.exists(dir_name):
                try:
                    os.makedirs(dir_name, exist_ok=True)
                except Exception:
                    # If we can't create the directory, let the original error propagate
                    pass
    
    return create_engine(database_url, connect_args={"check_same_thread": False})


engine = _get_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
