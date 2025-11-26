# app/database.py
from __future__ import annotations

from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import database_config
from app.domain.base import Base  # <-- shared Base


def create_connection_string() -> str:
    """Build connection string for MySQL using PyMySQL driver."""
    user = database_config["user"]
    password = quote_plus(database_config["password"])
    host = database_config["host"]
    port = database_config["port"]
    dbname = database_config["database"]

    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"


engine = create_engine(
    url=create_connection_string(),
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_session() -> Session:
    """Return a new DB session."""
    return SessionLocal()


def init_db() -> None:
    """
    Import all ORM models and create tables if they don't exist.
    """
    import app.domain.user        # noqa: F401
    import app.domain.portfolio   # noqa: F401
    import app.domain.security    # noqa: F401
    import app.domain.investment  # noqa: F401
    import app.domain.transaction # noqa: F401

    print("Metadata tables:", list(Base.metadata.tables.keys()))

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("✅ Database tables created / verified.")
