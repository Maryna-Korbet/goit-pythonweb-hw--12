import sys
import os
import asyncio
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from unittest.mock import AsyncMock

from main import app
from src.entity.models import Base, User, UserRole
from src.database.db import get_db
from src.services.auth_services import AuthService
from src.services.cache import CacheService, get_cache_service
from src.services.email_services import send_email


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678",
}


class FakeCacheService(CacheService):
    """Fake cache service."""
    def __init__(self):
        self._cache = {}
        self._blacklist = set()

    async def is_token_revoked(self, token: str) -> bool:
        return token in self._blacklist

    async def revoke_token(self, token: str, expire_at: datetime) -> None:
        self._blacklist.add(token)

    async def get_cached_user(self, username: str) -> User | None:
        return self._cache.get(f"user:{username}")

    async def cache_user(self, user: User) -> None:
        self._cache[f"user:{user.username}"] = user

    async def delete_user_cache(self, username: str) -> None:
        self._cache.pop(f"user:{username}", None)

    async def cleanup(self):
        """Clear cache and blacklist."""
        self._cache.clear()
        self._blacklist.clear()


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    """Initialize models."""
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async with TestingSessionLocal() as session:
            fake_cache = FakeCacheService()
            auth_service = AuthService(session, fake_cache)
            hash_password = auth_service._hash_password(test_user["password"])  # noqa

            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                hash_password=hash_password,
                confirmed=True,
                avatar="https://twitter.com/gravatar",
                role=UserRole.ADMIN,
            )
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    """Test client."""
    # Mock email service
    mock_send_email = AsyncMock()
    app.dependency_overrides[send_email] = lambda: mock_send_email

    # Dependency override
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    async def override_get_cache():
        fake_cache = FakeCacheService()
        try:
            yield fake_cache
        finally:
            await fake_cache.cleanup()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_cache_service] = override_get_cache

    yield TestClient(app)

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def get_token():
    """Get token."""
    async with TestingSessionLocal() as session:
        fake_cache = FakeCacheService()
        auth_service = AuthService(session, fake_cache)
        token = auth_service.create_access_token(test_user["username"])
        return token


@pytest.fixture(autouse=True)
async def cleanup_cache():
    """Cleanup cache."""
    fake_cache = FakeCacheService()
    yield
    await fake_cache.cleanup()