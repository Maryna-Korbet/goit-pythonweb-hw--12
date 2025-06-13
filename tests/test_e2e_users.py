import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.services.user_services import UserService
from src.schemas.user_schema import UserCreate
from src.entity.models import User

# ------------------ Fixtures ------------------

@pytest.fixture
def fake_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hash_password="hashedpass",
        role="user",
        avatar=None,
        confirmed=False,
    )


@pytest.fixture
def user_create_schema():
    return UserCreate(
        username="testuser",
        email="test@example.com",
        password="strongpassword"
    )


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_auth_service(fake_user):
    mock = AsyncMock()
    mock.register_user.return_value = fake_user
    return mock


@pytest.fixture
def mock_user_repo(fake_user):
    mock = AsyncMock()
    mock.get_by_username.return_value = fake_user
    mock.get_user_by_email.return_value = fake_user
    mock.update_avatar_url.return_value = fake_user
    return mock


# ------------------ Tests ------------------

@pytest.mark.asyncio
async def test_create_user(user_create_schema, fake_user, mock_db, mock_auth_service):
    with patch("src.service.auth_services.AuthService", return_value=mock_auth_service):
        service = UserService(db=mock_db)
        user = await service.create_user(user_create_schema)

        assert user.username == fake_user.username
        assert user.email == fake_user.email
        mock_auth_service.register_user.assert_called_once_with(user_create_schema)


@pytest.mark.asyncio
async def test_get_user_by_username(mock_db, mock_user_repo):
    with patch("src.services.user_service.UserRepository", return_value=mock_user_repo):
        service = UserService(db=mock_db)
        user = await service.get_user_by_username("testuser")

        assert user.username == "testuser"
        mock_user_repo.get_by_username.assert_called_once_with("testuser")


@pytest.mark.asyncio
async def test_get_user_by_email(mock_db, mock_user_repo):
    with patch("src.services.user_service.UserRepository", return_value=mock_user_repo):
        service = UserService(db=mock_db)
        user = await service.get_user_by_email("test@example.com")

        assert user.email == "test@example.com"
        mock_user_repo.get_user_by_email.assert_called_once_with("test@example.com")


@pytest.mark.asyncio
async def test_confirmed_email(mock_db, mock_user_repo):
    with patch("src.services.user_service.UserRepository", return_value=mock_user_repo):
        service = UserService(db=mock_db)
        await service.confirmed_email("test@example.com")

        mock_user_repo.confirmed_email.assert_called_once_with("test@example.com")


@pytest.mark.asyncio
async def test_update_avatar_url(mock_db, mock_user_repo):
    with patch("src.repositories.user_repository.UserRepository", return_value=mock_user_repo):
        service = UserService(db=mock_db)
        user = await service.update_avatar_url("test@example.com", None)

        assert user.username == "testuser"
        mock_user_repo.update_avatar_url.assert_called_once_with("test@example.com", None)


