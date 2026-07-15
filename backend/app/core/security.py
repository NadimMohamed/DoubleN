from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(
    subject: Any,
    expires_delta: Optional[timedelta] = None
) -> Tuple[str, int]:
    """
    Create access token.
    Returns: (token_string, expires_at_unix_timestamp)
    """
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    expires_at = int(expire.timestamp())
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": expires_at,
        "type": "access"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expires_at


def create_refresh_token(subject: Any) -> Tuple[str, int]:
    """
    Create refresh token.
    Returns: (token_string, expires_at_unix_timestamp)
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expires_at = int(expire.timestamp())
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": expires_at,
        "type": "refresh"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token, expires_at


def decode_token(token: str) -> dict:
    """Raises JWTError on invalid/expired token."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])


def get_token_expiry_timestamp(token: str) -> int:
    """Get 'exp' Unix timestamp from token payload. Returns 0 if invalid."""
    try:
        payload = decode_token(token)
        return payload.get("exp", 0)
    except JWTError:
        return 0
