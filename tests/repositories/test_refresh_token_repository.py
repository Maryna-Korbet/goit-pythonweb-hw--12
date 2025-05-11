import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, Mock

from src.entity.models import RefreshToken
from src.repositories.refresh_token_repository import RefreshTokenRepository

@pytest.fixture
def mock_session():
    """Mock session."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.add = Mock()
    return session

@pytest.fixture
def refresh_token_repository(mock_session):
    """Refresh token repository fixture."""
    return RefreshTokenRepository(mock_session)

@pytest.mark.asyncio
async def test_get_by_token_hash(refresh_token_repository, mock_session):
    """Get token by token hash."""
    # Arrange
    token_hash = "test_hash"
    mock_token = RefreshToken(token_hash=token_hash)
    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = mock_token
    mock_session.execute.return_value = mock_result

    # Act
    result = await refresh_token_repository.get_by_token_hash(token_hash)

    # Assert
    assert result == mock_token
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_active_token(refresh_token_repository, mock_session):
    """Get active token."""
    # Arrange
    token_hash = "test_hash"
    current_time = datetime.now()
    expired_at = current_time + timedelta(days=1)
    mock_token = RefreshToken(
        token_hash=token_hash,
        expired_at=expired_at,
        revoked_at=None
    )
    mock_result = Mock()
    mock_result.scalars.return_value.first.return_value = mock_token
    mock_session.execute.return_value = mock_result

    # Act
    result = await refresh_token_repository.get_active_token(token_hash, current_time)

    # Assert
    assert result == mock_token
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_save_token(refresh_token_repository, mock_session):
    """Save token."""
    # Arrange
    user_id = 1
    token_hash = "test_hash"
    expired_at = datetime.now() + timedelta(days=1)
    ip_address = "127.0.0.1"
    user_agent = "test_agent"
    mock_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expired_at=expired_at,
        ip_address=ip_address,
        user_agent=user_agent
    )
    mock_session.refresh.return_value = mock_token

    # Act
    result = await refresh_token_repository.save_token(
        user_id=user_id,
        token_hash=token_hash,
        expired_at=expired_at,
        ip_address=ip_address,
        user_agent=user_agent
    )

    # Assert
    assert result.user_id == mock_token.user_id
    assert result.token_hash == mock_token.token_hash
    assert result.expired_at == mock_token.expired_at
    assert result.ip_address == mock_token.ip_address
    assert result.user_agent == mock_token.user_agent
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_revoke_token(refresh_token_repository, mock_session):
    """Revoke token."""
    # Arrange
    mock_token = RefreshToken(
        token_hash="test_hash",
        expired_at=datetime.now() + timedelta(days=1),
        revoked_at=None
    )

    # Act
    await refresh_token_repository.revoke_token(mock_token)

    # Assert
    assert mock_token.revoked_at is not None
    mock_session.commit.assert_called_once() 