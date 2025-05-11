import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, Mock

from src.entity.models import User
from src.repositories.user_repository import UserRepository
from src.schemas.user_schema import UserCreate

@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = Mock()
    return session

@pytest.fixture
def user_repository(mock_session):
    """User repository fixture."""
    return UserRepository(mock_session)

@pytest.mark.asyncio
async def test_get_by_username(user_repository, mock_session):
    """Get user by username."""
    # Arrange
    username = "test_user"
    mock_user = User(username=username)
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result

    # Act
    result = await user_repository.get_by_username(username)

    # Assert
    assert result == mock_user
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session):
    """Get user by email."""
    # Arrange
    email = "test@example.com"
    mock_user = User(email=email)
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result

    # Act
    result = await user_repository.get_user_by_email(email)

    # Assert
    assert result == mock_user
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    """Create user."""
    # Arrange
    user_data = UserCreate(
        username="test_user",
        email="test@example.com",
        password="password123"
    )
    hashed_password = "hashed_password"
    avatar = "avatar_url"
    mock_user = User(
        username=user_data.username,
        email=user_data.email,
        hash_password=hashed_password,
        avatar=avatar
    )
    mock_session.refresh.return_value = mock_user

    # Act
    result = await user_repository.create_user(user_data, hashed_password, avatar)

    # Assert
    assert result.username == mock_user.username
    assert result.email == mock_user.email
    assert result.hash_password == mock_user.hash_password
    assert result.avatar == mock_user.avatar
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session):
    """Confirmed email."""
    # Arrange
    email = "test@example.com"
    mock_user = User(email=email, confirmed=False)
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result

    # Act
    await user_repository.confirmed_email(email)

    # Assert
    assert mock_user.confirmed is True
    mock_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session):
    """Update avatar URL."""
    # Arrange
    email = "test@example.com"
    new_url = "new_avatar_url"
    mock_user = User(email=email, avatar="old_url")
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result
    mock_session.refresh.return_value = mock_user

    # Act
    result = await user_repository.update_avatar_url(email, new_url)

    # Assert
    assert result.avatar == new_url
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once() 