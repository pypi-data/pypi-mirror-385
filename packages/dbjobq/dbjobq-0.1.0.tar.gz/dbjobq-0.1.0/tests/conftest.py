"""Pytest configuration and shared fixtures."""

import pytest
import pytest_asyncio

from dbjobq import JobQueue
from dbjobq.storage import SQLAlchemyStorage


@pytest.fixture
def temp_db():
    """Create a temporary in-memory SQLite database URL for testing."""
    # Use in-memory SQLite for faster tests
    return "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def storage(temp_db):
    """Create an async SQLAlchemy storage instance with in-memory database."""
    storage_instance = SQLAlchemyStorage(temp_db)
    await storage_instance.initialize()
    yield storage_instance
    await storage_instance.close()


@pytest_asyncio.fixture
async def job_queue(storage):
    """Create a JobQueue instance with a temporary storage backend."""
    return JobQueue(storage)


@pytest.fixture
def sample_job_data():
    """Sample job data for testing."""
    return {"name": "World", "count": 42, "items": ["a", "b", "c"]}
