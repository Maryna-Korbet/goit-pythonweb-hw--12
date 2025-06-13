from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.entity.models import User
from src.repositories.user_repository import UserRepository 
from src.schemas.user_schema import UserCreate
from src.services.auth_services import AuthService
from src.core.email_token import get_email_from_token
from src.services.email_services import send_email
from src.services.cache import get_cache_service
from src.config import messages


class UserService:
    """User service."""
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(self.db)
        self.auth_service = AuthService(db)

    async def create_user(self, user_data: UserCreate) -> User:
        """Create user."""
        user = await self.auth_service.register_user(user_data)
        return user

    async def get_user_by_username(self, username: str) -> User | None:
        """Get user by username."""
        cache = await get_cache_service()
        user = await cache.get_cached_user(username)
        if user:
            return user
        user = await self.user_repository.get_by_username(username)
        if user:
            await cache.cache_user(user)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        cache = await get_cache_service()
        user = await self.user_repository.get_user_by_email(email)
        if user:
            await cache.cache_user(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """Confirmed email."""
        await self.user_repository.confirmed_email(email)
        user = await self.user_repository.get_user_by_email(email)
        if user:
            cache = await get_cache_service()
            await cache.delete_user_cache(user.username)

    async def update_avatar_url(self, email: str, url: str):
        """Update avatar URL"""
        return await self.user_repository.update_avatar_url(email, url)

    async def request_password_reset(self, email: str, host: str):
        """Request password reset."""
        user = await self.user_repository.get_user_by_email(email)
        if user:
            await send_email(
                email=email,
                username=user.username,
                host=host,
                type_email="reset_password"
            )
        return {"message": messages.password_reset_email_sent.get("en")}

    async def reset_password(self, token: str, new_password: str):
        """Reset password."""
        email = get_email_from_token(token)
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.user_not_found.get("en"),
            )
        hashed_password = self.auth_service._hash_password(new_password)
        user.hash_password = hashed_password
        await self.db.commit()

        cache = await get_cache_service()
        await cache.delete_user_cache(user.username)
        return {"message": messages.password_reset_success.get("en")}