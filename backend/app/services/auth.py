from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import uuid
import structlog

from app.models.user import User
from app.core.security import hash_password, verify_password
from app.schemas.auth import UserRegister

log = structlog.get_logger(__name__)


class AuthService:

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_username(db: AsyncSession, username: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.username == username.lower()))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, data: UserRegister) -> User:
        # Check uniqueness
        existing_email = await AuthService.get_by_email(db, data.email)
        if existing_email:
            raise ValueError("An account with this email already exists")

        existing_username = await AuthService.get_by_username(db, data.username)
        if existing_username:
            raise ValueError("Username is already taken")

        user = User(
            email=data.email.lower(),
            username=data.username.lower(),
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            is_active=True,
            is_verified=False,  # Email verification in Phase 2
        )
        db.add(user)
        await db.flush()  # Get the ID without committing
        await db.refresh(user)
        log.info("user.created", user_id=str(user.id), email=user.email)
        return user

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await AuthService.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
