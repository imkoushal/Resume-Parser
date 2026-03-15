"""
auth.py - JWT authentication utilities.

Provides:
    - ``create_access_token()``  — generate a signed JWT
    - ``get_current_user()``     — FastAPI dependency (requires auth)
    - ``get_optional_user()``    — FastAPI dependency (auth is optional)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.core.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRY_MINUTES

# ---------------------------------------------------------------------------
# Security scheme
# ---------------------------------------------------------------------------

_security = HTTPBearer()
_security_optional = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Token creation
# ---------------------------------------------------------------------------

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a signed JWT token.

    Args:
        data: Claims to encode (must include ``"sub"`` with user email).
        expires_delta: Custom expiry; defaults to config value.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=JWT_EXPIRY_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> dict:
    """
    Decode and validate a JWT token. Returns the token payload.

    Raises HTTPException 401 if the token is missing, expired, or invalid.
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_security_optional),
) -> dict | None:
    """
    Same as ``get_current_user`` but returns ``None`` instead of raising
    if no token is provided. Used for endpoints with optional auth.
    """
    if credentials is None:
        return None

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
        )
        email: str | None = payload.get("sub")
        if email is None:
            return None
        return payload
    except JWTError:
        return None
