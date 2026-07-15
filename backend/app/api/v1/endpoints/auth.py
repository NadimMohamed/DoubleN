from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from datetime import timedelta, datetime, timezone
import structlog

from app.db.session import get_db
from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse,
    RefreshRequest, UserResponse,
)
from app.services.auth import AuthService
from app.core.security import (
    create_access_token, create_refresh_token,
    decode_token,
)
from app.core.exceptions import AuthenticationError, ConflictError
from app.api.v1.deps import get_current_user
from app.models.user import User

log = structlog.get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        user = await AuthService.create_user(db, data)
    except ValueError as e:
        log.warning("auth.register.conflict", email=data.email, reason=str(e))
        raise ConflictError(str(e))
    except SQLAlchemyError as e:
        log.error("auth.register.db_error", email=data.email, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create account") from e
    log.info("auth.register.success", user_id=str(user.id))
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive JWT tokens",
)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        user = await AuthService.authenticate(db, data.email, data.password)
    except SQLAlchemyError as e:
        log.error("auth.login.db_error", email=data.email, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to authenticate") from e

    if not user:
        log.warning("auth.login.failed", email=data.email, reason="invalid_credentials")
        raise AuthenticationError("Incorrect email or password")

    access_token, access_expires_at = create_access_token(user.id)
    refresh_token, refresh_expires_at = create_refresh_token(user.id)
    now = int(datetime.now(timezone.utc).timestamp())
    expires_in = access_expires_at - now

    log.info("auth.login.success", user_id=str(user.id), expires_in=expires_in)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        expires_at=access_expires_at,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using refresh token",
)
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    from jose import JWTError
    import uuid

    token_preview = (data.refresh_token or "")[:50]
    log.info("auth.refresh.attempt", token_preview=token_preview)

    try:
        payload = decode_token(data.refresh_token)
    except JWTError as e:
        log.warning("JWT validation failed", error=str(e), error_type=type(e).__name__, token_preview=token_preview)
        raise AuthenticationError("Invalid token format")

    log.info(
        "auth.refresh.decoded",
        payload={k: v for k, v in payload.items() if k not in ("sub",)},
        sub_present="sub" in payload,
        type_present="type" in payload,
    )

    try:
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        user_id = uuid.UUID(payload["sub"])
    except ValueError as e:
        log.warning("Invalid token type", error=str(e), error_type=type(e).__name__, token_type=payload.get("type"))
        raise AuthenticationError("Invalid token type")
    except KeyError as e:
        log.warning("Missing required token field", error=str(e), error_type=type(e).__name__)
        raise AuthenticationError("Invalid token format")

    try:
        user = await AuthService.get_by_id(db, user_id)
    except SQLAlchemyError as e:
        log.error("auth.refresh.db_error", user_id=str(user_id), error=str(e))
        raise HTTPException(status_code=500, detail="Failed to refresh token") from e

    if not user or not user.is_active:
        log.warning("auth.refresh.user_not_found_or_inactive", user_id=str(user_id))
        raise AuthenticationError("User not found")

    access_token, access_expires_at = create_access_token(user.id)
    refresh_token, refresh_expires_at = create_refresh_token(user.id)
    now = int(datetime.now(timezone.utc).timestamp())
    expires_in = access_expires_at - now

    log.info("auth.refresh.success", user_id=str(user.id), expires_in=expires_in)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
        expires_at=access_expires_at,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
