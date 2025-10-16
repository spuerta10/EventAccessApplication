from unittest.mock import ANY, AsyncMock
from uuid import uuid4

import pytest

from src.register_ticket_api.entities import Ticket, User
from src.register_ticket_api.exceptions import DbOperationException
from src.register_ticket_api.repositories.ticket_repository import TicketRepository


@pytest.fixture
def sample_user() -> User:
    return User(id=uuid4(), username="test", password="")


@pytest.fixture
def sample_ticket() -> Ticket:
    return Ticket(
        id=uuid4(),
        seat="A1",
        gate="G1",
        seed=b"seed_data",
        status="valid",
        created_at="2024-01-01T00:00:00Z",
        used_at=None,
        user_id=None,
    )


@pytest.fixture
def mock_db_context() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def ticket_repository(mock_db_context: AsyncMock) -> TicketRepository:
    return TicketRepository(db_context=mock_db_context)


async def test_register_ticket_calls_stored_procedure(
    mock_db_context: AsyncMock,
    sample_user: User,
    sample_ticket: Ticket,
    ticket_repository: TicketRepository,
) -> None:
    mock_conn = AsyncMock()
    mock_conn.execute.return_value = 1  # emulates 1 affected row
    mock_db_context.get_connection.return_value = mock_conn

    result: bool = await ticket_repository.register_ticket(user=sample_user, ticket=sample_ticket)

    mock_conn.execute.assert_awaited_once_with(
        "CALL sp_register_ticket_to_user($1, $2)",
        sample_ticket.id,
        sample_user.id,
    )
    assert result is True


async def test_mark_ticket_as_used_calls_function(
    mock_db_context: AsyncMock, ticket_repository: TicketRepository, sample_ticket: Ticket
) -> None:
    mock_conn = AsyncMock()
    mock_conn.fetchval.return_value = True
    mock_db_context.get_connection.return_value = mock_conn

    result = await ticket_repository.mark_ticket_as_used(sample_ticket.id)

    mock_conn.fetchval.assert_awaited_once_with(
        "SELECT fn_mark_ticket_as_used($1)", sample_ticket.id
    )
    assert result is True


async def test_get_by_ticket_details_returns_ticket(
    mock_db_context: AsyncMock, sample_ticket: Ticket, ticket_repository: TicketRepository
) -> None:
    mock_conn = AsyncMock()
    mock_db_context.get_connection.return_value = mock_conn
    mock_conn.fetchrow.return_value = sample_ticket.model_dump()

    ticket: Ticket = await ticket_repository.get_by_ticket_details(
        seat=sample_ticket.seat, gate=sample_ticket.gate
    )

    mock_conn.fetchrow.assert_awaited_once_with(ANY, sample_ticket.seat, sample_ticket.gate)
    assert isinstance(ticket, Ticket)
    assert ticket.seat == sample_ticket.seat
    assert ticket.gate == sample_ticket.gate


async def test_get_by_ticket_details_returns_none_when_not_found(
    mock_db_context: AsyncMock, ticket_repository: TicketRepository
) -> None:
    mock_conn = AsyncMock()
    mock_db_context.get_connection.return_value = mock_conn
    mock_conn.fetchrow.return_value = None

    result = await ticket_repository.get_by_ticket_details("X1", "G9")

    assert result is None
    mock_conn.fetchrow.assert_awaited_once()


async def test_get_by_ticket_details_raises_db_operation_exception(
    mock_db_context: AsyncMock, ticket_repository: TicketRepository
) -> None:
    mock_conn = AsyncMock()
    mock_db_context.get_connection.return_value = mock_conn
    mock_conn.fetchrow.side_effect = Exception("DB error")

    with pytest.raises(DbOperationException):
        await ticket_repository.get_by_ticket_details("A1", "G1")
