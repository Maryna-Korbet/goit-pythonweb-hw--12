import redis.asyncio as Redis
from datetime import datetime, timezone
from src.config.config import settings
from src.entity.models import User
from src.schemas.user_schema import UserResponse


class CacheService:
    """Redis cache service."""
    def __init__(self):
        """Initialize Redis client with application settings."""
        self.redis: Redis = Redis.from_url(settings.REDIS_URL)
        self.cache_ttl: int = settings.REDIS_TTL

    async def is_token_revoked(self, token: str) -> bool:
        """Check if a token has been revoked."""
        result = await self.redis.exists(f"black-list:{token}")
        return bool(result)

    async def revoke_token(self, token: str, expire_at: datetime) -> None:
        """Revoke token."""
        now = datetime.now(timezone.utc)

        if expire_at > now:
            ttl = int((expire_at - datetime.now(timezone.utc)).total_seconds())
            await self.redis.setex(f"black-list:{token}", ttl, "1")

    async def get_cached_user(self, username: str) -> User | None:
        """Get user data from cache."""
        cached_user = await self.redis.get(f"user:{username}")
        if cached_user:
            try:
                user_data = UserResponse.model_validate_json(cached_user.decode("utf-8"))
                return User(**user_data.model_dump())
            except Exception:
                return None
        return None

    async def cache_user(self, user: User) -> None:
        """Cache user data."""
        user_data = UserResponse.from_orm(user)
        await self.redis.setex(
            f"user:{user.username}", 
            self.cache_ttl, user_data.model_dump_json()
        )

    async def delete_user_cache(self, username: str) -> None:
        """Delete user data from cache."""
        await self.redis.delete(f"user:{username}")


cache_service = CacheService()


async def get_cache_service() -> CacheService:
    """Get cache service instance."""
    return cache_service