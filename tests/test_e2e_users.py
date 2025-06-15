import pytest
from unittest.mock import AsyncMock, patch

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
    db = AsyncMock()  
    return db


@pytest.fixture
def mock_auth_service(fake_user):
    mock = AsyncMock()
    mock.register_user.return_value = fake_user
    return mock


@pytest.fixture
def mock_user_repo(fake_user):
    mock = AsyncMock()
    mock.get_by_username = AsyncMock(return_value=fake_user)
    mock.get_user_by_email = AsyncMock(return_value=fake_user)
    mock.update_avatar_url = AsyncMock(return_value=fake_user)
    mock.confirmed_email = AsyncMock()
    return mock


# ------------------ Tests ------------------

@patch("src.services.auth_services.AuthService")
@patch("src.repositories.user_repository.UserRepository")
@pytest.mark.asyncio
async def test_create_user(mock_user_repo_class, mock_auth_service_class, user_create_schema, fake_user, mock_db):
    # Підробка репозиторію: користувача ще не існує
    mock_user_repo = AsyncMock()
    mock_user_repo.get_by_username = AsyncMock(return_value=None)
    mock_user_repo.get_user_by_email = AsyncMock(return_value=None)
    mock_user_repo_class.return_value = mock_user_repo

    # Підробка auth-сервісу
    mock_auth_service = AsyncMock()
    mock_auth_service.register_user = AsyncMock(return_value=fake_user)
    mock_auth_service_class.return_value = mock_auth_service

    service = UserService(db=mock_db)
    user = await service.create_user(user_create_schema)

    assert user.username == fake_user.username
    assert user.email == fake_user.email
    mock_auth_service.register_user.assert_awaited_once_with(user_create_schema)

@patch("src.services.user_services.get_cache_service", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_get_user_by_username(mock_cache_service, mock_db, mock_user_repo, fake_user):
    mock_cache = AsyncMock()
    mock_cache.get_cached_user.return_value = None
    mock_cache.cache_user.return_value = None
    mock_cache_service.return_value = mock_cache

    with patch("src.services.user_services.UserRepository", return_value=mock_user_repo):
        service = UserService(db=mock_db)
        user = await service.get_user_by_username("testuser")

        assert user.username == fake_user.username
        mock_user_repo.get_by_username.assert_awaited_once_with("testuser")


@patch("src.services.user_services.get_cache_service", new_callable=AsyncMock)
@pytest.mark.asyncio
async def test_get_user_by_email(mock_cache_service, mock_db, mock_user_repo, fake_user):
    mock_cache = AsyncMock()
    mock_cache.cache_user.return_value = None
    mock_cache_service.return_value = mock_cache

    with patch("src.services.user_services.UserRepository", return_value=mock_user_repo):
        service = UserService(db=mock_db)
        user = await service.get_user_by_email("test@example.com")

        assert user.email == fake_user.email
        mock_user_repo.get_user_by_email.assert_awaited_once_with("test@example.com")
        mock_cache.cache_user.assert_awaited_once_with(fake_user)


@pytest.mark.asyncio
async def test_confirmed_email(mock_db, mock_user_repo):
    with patch("src.services.user_services.UserRepository", return_value=mock_user_repo):
        service = UserService(db=mock_db)
        await service.confirmed_email("test@example.com")

        mock_user_repo.confirmed_email.assert_called_once_with("test@example.com")


@pytest.mark.asyncio
async def test_update_avatar_url(mock_db, mock_user_repo, fake_user):
    with patch("src.repositories.user_repository.UserRepository", return_value=mock_user_repo):
        service = UserService(db=mock_db)
        user = await service.update_avatar_url("test@example.com", None)

        assert user.username == fake_user.username
        mock_user_repo.update_avatar_url.assert_awaited_once_with("test@example.com", None)


