from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.register_ticket_api.entities import User
from src.register_ticket_api.infraestructure import PostgreSQLDbContext
from src.register_ticket_api.repositories import UserRepository

# Test data constants
TEST_USERNAME: str = "test_user"
TEST_PASSWORD: str = ""
TEST_USER_ID: str = str(uuid4())
SP_INSERT_USER: str = "sp_insert_user"


@pytest.fixture
def mock_db_context() -> AsyncMock:
    """Mock PostgreSQL database context."""
    return AsyncMock(spec=PostgreSQLDbContext)


@pytest.fixture
def mock_db_connection() -> AsyncMock:
    """Mock database connection."""
    return AsyncMock()


@pytest.fixture
def user_repository(mock_db_context: AsyncMock) -> UserRepository:
    """Create UserRepository instance with mocked database context."""
    return UserRepository(db_context=mock_db_context)


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    return User(id=uuid4(), username=TEST_USERNAME, password=TEST_PASSWORD)


async def test_get_by_username_success(
    user_repository: UserRepository,
    mock_db_context: AsyncMock,
    mock_db_connection: AsyncMock,
) -> None:
    """Test successful user retrieval by username."""
    expected_row = {
        "id": TEST_USER_ID,
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
    }
    mock_db_connection.fetchrow.return_value = expected_row
    mock_db_context.get_connection.return_value = mock_db_connection

    result = await user_repository.get_by_username(TEST_USERNAME)

    assert result is not None
    assert result.username == TEST_USERNAME
    assert result.password == TEST_PASSWORD
    assert str(result.id) == TEST_USER_ID
    mock_db_context.get_connection.assert_called_once()
    mock_db_connection.fetchrow.assert_called_once()
    # Verify the query uses LOWER() for case-insensitive search
    call_args = mock_db_connection.fetchrow.call_args
    assert "LOWER(username)" in call_args[0][0]
    assert "LOWER($1)" in call_args[0][0]
    assert call_args[0][1] == TEST_USERNAME


async def test_get_by_username_case_insensitive(
    user_repository: UserRepository,
    mock_db_context: AsyncMock,
    mock_db_connection: AsyncMock,
) -> None:
    """Test that username search is case-insensitive."""
    expected_row = {
        "id": TEST_USER_ID,
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
    }
    mock_db_connection.fetchrow.return_value = expected_row
    mock_db_context.get_connection.return_value = mock_db_connection

    # Search with uppercase username
    result = await user_repository.get_by_username("TEST_USER")

    assert result is not None
    assert result.username == TEST_USERNAME
    mock_db_connection.fetchrow.assert_called_once()


async def test_get_by_username_not_found(
    user_repository: UserRepository,
    mock_db_context: AsyncMock,
    mock_db_connection: AsyncMock,
) -> None:
    """Test user retrieval returns None when user does not exist."""
    mock_db_connection.fetchrow.return_value = None
    mock_db_context.get_connection.return_value = mock_db_connection

    result = await user_repository.get_by_username("nonexistent_user")

    assert result is None
    mock_db_context.get_connection.assert_called_once()
    mock_db_connection.fetchrow.assert_called_once()


async def test_create_user_success(
    user_repository: UserRepository,
    mock_db_context: AsyncMock,
    mock_db_connection: AsyncMock,
    sample_user: User,
) -> None:
    """Test successful user creation."""
    mock_db_connection.execute.return_value = "CREATE"  # Non-zero rows affected
    mock_db_context.get_connection.return_value = mock_db_connection

    result = await user_repository.create_user(sample_user)

    assert result is True
    mock_db_context.get_connection.assert_called_once()
    mock_db_connection.execute.assert_called_once()

    # Verify stored procedure call
    call_args = mock_db_connection.execute.call_args
    assert f"CALL {SP_INSERT_USER}($1, $2)" in call_args[0][0]
    assert call_args[0][1] == sample_user.username
    assert call_args[0][2] == sample_user.password


async def test_create_user_no_rows_affected(
    user_repository: UserRepository,
    mock_db_context: AsyncMock,
    mock_db_connection: AsyncMock,
    sample_user: User,
) -> None:
    """Test user creation returns False when no rows are affected."""
    mock_db_connection.execute.return_value = 0
    mock_db_context.get_connection.return_value = mock_db_connection

    result = await user_repository.create_user(sample_user)

    assert result is False
    mock_db_context.get_connection.assert_called_once()
    mock_db_connection.execute.assert_called_once()
