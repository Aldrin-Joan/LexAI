import os
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback/default SQLite for local testing if DATABASE_URL is not set
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./local_db.db"

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=True)


def init_db() -> None:
    """Create database tables if they do not exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency for DB session.

    Yields:
        Session: SQLModel database session.
    """
    with Session(engine) as session:
        yield session
