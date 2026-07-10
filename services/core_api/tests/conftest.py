"""Shared pytest configuration for core_api tests.

This conftest is loaded by pytest before any test module is collected,
which means:
1. DEV_BYPASS_AUTH and ENV are set in os.environ before ``app.main``
   is imported for the first time, ensuring the security module picks
   them up at module-level evaluation time.
2. An in-memory SQLite engine is wired into the app's get_session
   dependency so tests never touch the real database file.

sys.path
--------
``pyproject.toml`` sets ``pythonpath = ["."]``, which adds
``services/core_api`` to sys.path before any collection starts.
If you are running pytest from a different working directory, set
PYTHONPATH manually:
    PYTHONPATH=. uv run pytest tests/ -v
"""

import os
import sys

# ---------------------------------------------------------------------------
# Path guard — ensure the project root is importable even if pyproject.toml
# pythonpath hasn't been applied (e.g. direct `python -m pytest` invocations).
# ---------------------------------------------------------------------------

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# ---------------------------------------------------------------------------
# Environment must be patched BEFORE app modules are imported so that
# module-level os.getenv() calls in security.py / main.py see the test values.
# ---------------------------------------------------------------------------

os.environ.setdefault("DEV_BYPASS_AUTH", "true")
os.environ.setdefault("ENV", "development")
os.environ.setdefault("DEV_USER_UID", "default-test-uid")
os.environ.setdefault("DEV_USER_EMAIL", "test@lexai.test")
os.environ.setdefault("DEV_USER_NAME", "Test User")
os.environ.setdefault("DEV_USER_IS_LAWYER", "false")
# Point to in-memory SQLite so tests never touch data/index.db
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# In-memory SQLite engine — shared across the entire test session.
# Using StaticPool ensures all connections share the same database.
# ---------------------------------------------------------------------------

_TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)


def _get_test_session():
    """Dependency override — yield a session from the in-memory engine."""
    with Session(_TEST_ENGINE) as session:
        yield session


# ---------------------------------------------------------------------------
# Session-scoped fixture that initialises tables and wires the override.
# All test modules that need the app client inherit from this automatically
# because it is autouse=True at session scope.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def _setup_test_db():
    """Create all tables on the in-memory engine before any test runs."""
    # Import happens here (after env vars are set above) so security.py
    # and db.py read the patched environment correctly.
    from app.core.db import get_session
    from app.main import app as fastapi_app
    import app.models.models  # Ensure all model tables are registered in metadata

    # Wire the in-memory session into the FastAPI dependency system
    fastapi_app.dependency_overrides[get_session] = _get_test_session

    # Create tables (safe to call multiple times — SQLModel is idempotent)
    SQLModel.metadata.create_all(_TEST_ENGINE)

    yield  # all tests run here

    # Teardown
    SQLModel.metadata.drop_all(_TEST_ENGINE)
    fastapi_app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Expose the test engine so individual test modules can seed rows directly.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def test_engine():
    """Return the shared in-memory SQLite engine."""
    return _TEST_ENGINE
