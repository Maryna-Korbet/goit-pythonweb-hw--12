from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.repositories.user_repository import UserRepository 
from src.schemas.user_schema import UserCreate
from src.services.auth_services import AuthService


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
        user = await self.user_repository.get_by_username(username)
        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email."""
        user = await self.user_repository.get_user_by_email(email)
        return user

    async def confirmed_email(self, email: str) -> None:
        """Confirmed email."""
        user = await self.user_repository.confirmed_email(email)
        return user

    async def update_avatar_url(self, email: str, url: str):
        """Update avatar URL"""
        return await self.user_repository.update_avatar_url(email, url)