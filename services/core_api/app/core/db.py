"""Database engine configuration for the LegalTech Super-App."""

import os
from typing import Generator

from sqlalchemy import event
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback to local SQLite when DATABASE_URL is not set
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./local_db.db"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=True)


# ---------------------------------------------------------------------------
# SQLite performance: Write-Ahead Logging (WAL)
# Dramatically reduces write contention for concurrent P2P chat workloads.
# This is a no-op when DATABASE_URL points at PostgreSQL.
# ---------------------------------------------------------------------------

@event.listens_for(engine, "connect")
def set_sqlite_pragma(
    dbapi_connection: object, connection_record: object
) -> None:
    """Set SQLite pragmas for WAL mode and normal synchronization.

    Args:
        dbapi_connection: The raw DBAPI connection object.
        connection_record: The connection pool record.
    """
    if DATABASE_URL.startswith("sqlite"):
        cursor = dbapi_connection.cursor()  # type: ignore[union-attr]
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


def init_db() -> None:
    """Create database tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session.

    Yields:
        Session: An active SQLModel database session.
    """
    with Session(engine) as session:
        yield session
