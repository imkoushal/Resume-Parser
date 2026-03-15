"""
user_service.py - User management service.

Handles user registration, authentication, and lookup.
Passwords are hashed using passlib with bcrypt.
"""

from passlib.context import CryptContext

from src.core.database import users_collection
from src.models.db_models import create_user_document

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hash."""
    return _pwd_context.verify(plain_password, hashed_password)


# ---------------------------------------------------------------------------
# User operations
# ---------------------------------------------------------------------------

async def get_user_by_email(email: str) -> dict | None:
    """Look up a user by email. Returns the document or None."""
    return await users_collection().find_one({"email": email})


async def create_user(email: str, password: str, full_name: str) -> dict:
    """
    Register a new user.

    Args:
        email: User's email address (used as unique identifier).
        password: Plaintext password (will be hashed before storage).
        full_name: User's display name.

    Returns:
        The inserted user document (with ``_id``).

    Raises:
        ValueError: If the email is already registered.
    """
    existing = await get_user_by_email(email)
    if existing is not None:
        raise ValueError("Email already registered")

    hashed = hash_password(password)
    doc = create_user_document(email, hashed, full_name)
    result = await users_collection().insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc


async def authenticate_user(email: str, password: str) -> dict | None:
    """
    Authenticate a user by email and password.

    Returns:
        The user document if credentials are valid, else None.
    """
    user = await get_user_by_email(email)
    if user is None:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user
