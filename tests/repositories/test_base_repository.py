import pytest
from unittest.mock import AsyncMock, Mock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta, declarative_base
from sqlalchemy import Column, Integer, String

from src.repositories.base_repository import BaseRepository

Base: DeclarativeMeta = declarative_base()


class DummyModel(Base):
    __tablename__ = "dummy"
    id = Column(Integer, primary_key=True)
    name = Column(String)


@pytest.fixture
def dummy_instance():
    """Dummy model instance."""
    return DummyModel(id=1, name="Test Name")


@pytest.fixture
def mock_session():
    """Mock session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def repository(mock_session):
    """Base repository fixture."""
    return BaseRepository(session=mock_session, model=DummyModel)


@pytest.mark.asyncio
async def test_get_all(repository, mock_session, dummy_instance):
    """Get all entities."""
    scalars_mock = Mock()
    scalars_mock.all.return_value = [dummy_instance]

    mock_result = Mock()
    mock_result.scalars.return_value = scalars_mock

    mock_session.execute.return_value = mock_result

    result = await repository.get_all()

    mock_session.execute.assert_called_once()
    assert result == [dummy_instance]


@pytest.mark.asyncio
async def test_get_by_id(repository, mock_session, dummy_instance):
    """Get entity by id."""
    scalars_mock = Mock()
    scalars_mock.first.return_value = dummy_instance

    mock_result = Mock()
    mock_result.scalars.return_value = scalars_mock

    mock_session.execute.return_value = mock_result

    result = await repository.get_by_id(1)

    mock_session.execute.assert_called_once()
    assert result == dummy_instance


@pytest.mark.asyncio
async def test_create(repository, mock_session, dummy_instance):
    """Create entity."""
    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    result = await repository.create(dummy_instance)

    mock_session.add.assert_called_once_with(dummy_instance)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(dummy_instance)
    assert result == dummy_instance


@pytest.mark.asyncio
async def test_update(repository, mock_session, dummy_instance):
    """Update entity."""
    mock_session.commit.return_value = None
    mock_session.refresh.return_value = None

    result = await repository.update(dummy_instance)

    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(dummy_instance)
    assert result == dummy_instance


@pytest.mark.asyncio
async def test_delete(repository, mock_session, dummy_instance):
    """Delete entity."""
    mock_session.delete.return_value = None
    mock_session.commit.return_value = None

    await repository.delete(dummy_instance)

    mock_session.delete.assert_called_once_with(dummy_instance)
    mock_session.commit.assert_called_once()