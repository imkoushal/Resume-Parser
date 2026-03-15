"""
database.py - MongoDB connection management using Motor (async driver).

Provides:
    - ``connect_db()`` / ``close_db()`` — startup/shutdown lifecycle hooks
    - ``get_database()`` — returns the Motor database instance
    - Collection accessors: ``users_collection``, ``resumes_collection``,
      ``analysis_collection``
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.core.config import MONGODB_URL, MONGODB_DATABASE

# ---------------------------------------------------------------------------
# Module-level state (initialised via lifecycle hooks)
# ---------------------------------------------------------------------------

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


# ---------------------------------------------------------------------------
# Lifecycle hooks (called from app.py)
# ---------------------------------------------------------------------------

async def connect_db() -> None:
    """Open the Motor client and select the database."""
    global _client, _database
    _client = AsyncIOMotorClient(MONGODB_URL)
    _database = _client[MONGODB_DATABASE]


async def close_db() -> None:
    """Close the Motor client."""
    global _client, _database
    if _client is not None:
        _client.close()
    _client = None
    _database = None


# ---------------------------------------------------------------------------
# Accessors
# ---------------------------------------------------------------------------

def get_database() -> AsyncIOMotorDatabase:
    """Return the active database instance."""
    if _database is None:
        raise RuntimeError(
            "Database not initialised. Call connect_db() first."
        )
    return _database


def users_collection():
    """Return the 'users' collection."""
    return get_database()["users"]


def resumes_collection():
    """Return the 'resumes' collection."""
    return get_database()["resumes"]


def analysis_collection():
    """Return the 'analysis_results' collection."""
    return get_database()["analysis_results"]
