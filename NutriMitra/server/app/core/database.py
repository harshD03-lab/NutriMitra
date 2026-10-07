import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


def _get_engine():
    database_url = settings.DATABASE_URL
    
    # Handle plain file paths (assume SQLite)
    if not database_url.startswith("sqlite:///"):
        # Treat as a plain file path for SQLite database
        # Make it absolute if it's relative
        if not os.path.isabs(database_url):
            database_url = os.path.abspath(database_url)
        # Convert to SQLAlchemy SQLite URL
        database_url = f"sqlite:///{database_url}"
    
    # Handle relative paths for SQLite (sqlite:/// prefix)
    if database_url.startswith("sqlite:///") and not database_url.startswith("sqlite:////"):
        # Convert relative path to absolute path for SQLAlchemy
        if database_url == "sqlite:///./nutrimitra.db":
            # Make it absolute based on current working directory
            abs_path = os.path.abspath("./nutrimitra.db")
            database_url = f"sqlite:///{abs_path}"
        elif database_url.startswith("sqlite:///."):
            # Handle other relative paths like sqlite:///../file.db
            relative_path = database_url[9:]  # Remove sqlite:/// prefix
            abs_path = os.path.abspath(relative_path)
            database_url = f"sqlite:///{abs_path}"
    
    # For SQLite URLs, ensure the directory exists
    if database_url.startswith("sqlite:///"):
        # Extract the file path from sqlite:///path/to/file.db
        # sqlite:/// -> 9 chars for sqlite:///
        if database_url.startswith("sqlite:////"):
            # Absolute path: sqlite:////tmp/file.db -> /tmp/file.db
            file_path = database_url[10:]  # Remove sqlite://// prefix
        else:
            # Relative or absolute path: sqlite:///path/to/file.db
            file_path = database_url[9:]   # Remove sqlite:/// prefix
        
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
