import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings


def _resolve_database_url(raw: str) -> str:
    """Turn the configured DATABASE_URL into a usable SQLAlchemy URL.

    ``DATABASE_URL`` may be a real URL (``postgresql://...``), a SQLite URL
    (``sqlite:///path.db``) or a plain file path.  Plain paths are treated as
    SQLite, real URLs are passed through untouched so that a hosted database
    (for example Postgres on Vercel) can be used without code changes.
    """
    url = raw.strip()
    if not url:
        raise ValueError("DATABASE_URL is empty")
    if url.startswith("sqlite:///"):
        path = url[len("sqlite:///"):]
        if path and not os.path.isabs(path):
            path = os.path.abspath(path)
        url = f"sqlite:///{path}"
        return url
    if "://" in url:
        # postgresql://, mysql://, ... - leave it alone.
        return url
    # Plain file path -> SQLite.
    return f"sqlite:///{os.path.abspath(url)}"


def _get_engine():
    database_url = _resolve_database_url(settings.DATABASE_URL)

    if not database_url.startswith("sqlite"):
        # Hosted database: enable a pre-ping so stale connections are recycled.
        # Serverless platforms (Vercel) must not keep a connection pool per
        # invocation, so use NullPool there and rely on the provider's pooler.
        if os.getenv("VERCEL"):
            return create_engine(
                database_url, pool_pre_ping=True, poolclass=NullPool
            )
        return create_engine(database_url, pool_pre_ping=True)

    # For SQLite URLs, ensure the directory exists.
    file_path = database_url[len("sqlite:///"):]
    dir_name = os.path.dirname(file_path)
    if dir_name and not os.path.exists(dir_name):
        try:
            os.makedirs(dir_name, exist_ok=True)
        except OSError:
            # If we can't create the directory, let the original error propagate.
            pass

    return create_engine(database_url, connect_args={"check_same_thread": False})


engine = _get_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


# Columns added after the first release.  ``create_all`` only creates missing
# tables, so existing databases need these columns added explicitly.
COLUMN_MIGRATIONS: dict[str, list[tuple[str, str]]] = {
    "users": [
        ("allergies", "VARCHAR"),
    ],
    "food_items": [
        ("sugar_g", "FLOAT"),
        ("sodium_mg", "FLOAT"),
    ],
}


def ensure_schema(target_engine=None) -> list[str]:
    """Add any missing columns to already existing tables.

    Returns the list of applied migrations so the caller can log them.
    """
    target_engine = target_engine or engine
    applied: list[str] = []
    inspector = inspect(target_engine)
    existing_tables = set(inspector.get_table_names())
    for table, columns in COLUMN_MIGRATIONS.items():
        if table not in existing_tables:
            continue
        present = {col["name"] for col in inspector.get_columns(table)}
        for name, ddl_type in columns:
            if name in present:
                continue
            with target_engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl_type}"))
            applied.append(f"{table}.{name}")
    return applied


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
