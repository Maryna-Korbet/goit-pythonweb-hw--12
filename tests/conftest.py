import asyncio

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
from src.services.email_services import send_email


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
    "username": "anna",
    "email": "anna@example.com",
    "password": "12345678",
}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    """Init models."""
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        async with TestingSessionLocal() as session:
            auth_service = AuthService(session, None)  
            hash_password = auth_service._hash_password(test_user["password"])  

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
    """Client fixture."""  
    # Mock email service
    mock_send_email = AsyncMock()
    app.dependency_overrides[send_email] = lambda: mock_send_email

    # Dependency override for the database
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def get_token():
    """Get token."""
    async with TestingSessionLocal() as session:
        auth_service = AuthService(session, None) 
        token = auth_service.create_access_token(test_user["username"])
        return token