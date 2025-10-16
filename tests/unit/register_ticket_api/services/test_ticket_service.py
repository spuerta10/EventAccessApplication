from base64 import b64encode
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from src.register_ticket_api.entities import AttendanceLog, Ticket, User
from src.register_ticket_api.exceptions import AppValidationException, DbOperationException
from src.register_ticket_api.repositories import TicketRepository, UserRepository
from src.register_ticket_api.services import TicketService

# Test data constants
VALID_SEED_BYTES: bytes = b"test_secret_key_"
VALID_SEED_BASE64: str = b64encode(VALID_SEED_BYTES).decode("utf-8")
TEST_SEAT: str = "A1"
TEST_GATE: str = "G1"
TOTP_INTERVAL: int = 60


@pytest.fixture
def sample_user() -> User:
    """Create a sample user for testing."""
    return User(id=uuid4(), username="test_user", password="")


@pytest.fixture
def sample_ticket() -> Ticket:
    """Create a sample ticket without user assigned."""
    return Ticket(
        id=uuid4(),
        seat=TEST_SEAT,
        gate=TEST_GATE,
        seed=None,
        status="valid",
        created_at="2024-01-01T00:00:00Z",
        used_at=None,
        user_id=None,
    )


@pytest.fixture
def sample_registered_ticket(sample_ticket: Ticket, sample_user: User) -> Ticket:
    """Create a registered ticket with user and seed."""
    registered_ticket: Ticket = sample_ticket.model_copy()
    registered_ticket.user_id = sample_user.id
    registered_ticket.seed = VALID_SEED_BASE64
    return registered_ticket


@pytest.fixture
def sample_attendance_log(sample_ticket: Ticket) -> AttendanceLog:
    """Create a sample attendance log."""
    return AttendanceLog(seat=sample_ticket.seat, gate=sample_ticket.gate, totp_code="123456")


@pytest.fixture
def mock_user_repo() -> AsyncMock:
    """Mock user repository."""
    return AsyncMock(spec=UserRepository)


@pytest.fixture
def mock_ticket_repo() -> AsyncMock:
    """Mock ticket repository."""
    return AsyncMock(spec=TicketRepository)


@pytest.fixture
def ticket_service(mock_user_repo: AsyncMock, mock_ticket_repo: AsyncMock) -> TicketService:
    """Create TicketService instance with mocked repositories."""
    return TicketService(user_repo=mock_user_repo, ticket_repo=mock_ticket_repo)


# ==================== Tests for register_ticket ====================


async def test_register_ticket_success(  # noqa: PLR0913
    ticket_service: TicketService,
    mock_user_repo: AsyncMock,
    mock_ticket_repo: AsyncMock,
    sample_user: User,
    sample_ticket: Ticket,
    sample_registered_ticket: Ticket,
) -> None:
    """Test successful ticket registration."""
    mock_user_repo.get_by_username.return_value = sample_user
    mock_ticket_repo.get_by_ticket_details.side_effect = [sample_ticket, sample_registered_ticket]
    mock_ticket_repo.register_ticket.return_value = True

    result = await ticket_service.register_ticket(sample_user.username, sample_ticket)

    assert result == sample_registered_ticket
    assert result.user_id == sample_user.id
    mock_user_repo.get_by_username.assert_called_once_with(sample_user.username)
    mock_ticket_repo.register_ticket.assert_called_once_with(sample_user, sample_ticket)


async def test_register_ticket_user_not_found(
    ticket_service: TicketService,
    mock_user_repo: AsyncMock,
    sample_user: User,
    sample_ticket: Ticket,
) -> None:
    """Test ticket registration fails when user does not exist."""
    mock_user_repo.get_by_username.return_value = None

    with pytest.raises(AppValidationException, match="User .* does not exist"):
        await ticket_service.register_ticket(sample_user.username, sample_ticket)

    mock_user_repo.get_by_username.assert_called_once_with(sample_user.username)


# async def test_register_ticket_invalid_ticket_details(
#    ticket_service: TicketService,
#    mock_user_repo: AsyncMock,
#    sample_user: User,
# ) -> None:
#    """Test ticket registration fails with invalid ticket details."""
#    mock_user_repo.get_by_username.return_value = sample_user
#    invalid_ticket = Ticket(
#        id=uuid4(),
#        seat="",  # Empty seat should be invalid
#        gate=TEST_GATE,
#        user_id=None,
#        seed=None,
#        status="valid",
#        created_at="2024-01-01T00:00:00Z",
#        used_at=None,
#    )

#    with pytest.raises(AppValidationException, match="Invalid ticket details"):
#        await ticket_service.register_ticket(sample_user.username, invalid_ticket)


async def test_register_ticket_not_exists_in_db(
    ticket_service: TicketService,
    mock_user_repo: AsyncMock,
    mock_ticket_repo: AsyncMock,
    sample_user: User,
    sample_ticket: Ticket,
) -> None:
    """Test ticket registration fails when ticket does not exist in database."""
    mock_user_repo.get_by_username.return_value = sample_user
    mock_ticket_repo.get_by_ticket_details.return_value = None

    with pytest.raises(AppValidationException, match="Ticket does not exist"):
        await ticket_service.register_ticket(sample_user.username, sample_ticket)


async def test_register_ticket_already_registered(  # noqa: PLR0913
    ticket_service: TicketService,
    mock_user_repo: AsyncMock,
    mock_ticket_repo: AsyncMock,
    sample_user: User,
    sample_ticket: Ticket,
    sample_registered_ticket: Ticket,
) -> None:
    """Test ticket registration fails when ticket is already registered."""
    mock_user_repo.get_by_username.return_value = sample_user
    mock_ticket_repo.get_by_ticket_details.return_value = sample_registered_ticket

    with pytest.raises(AppValidationException, match="Ticket is already registered"):
        await ticket_service.register_ticket(sample_user.username, sample_ticket)


async def test_register_ticket_db_operation_exception(
    ticket_service: TicketService,
    mock_user_repo: AsyncMock,
    mock_ticket_repo: AsyncMock,
    sample_user: User,
    sample_ticket: Ticket,
) -> None:
    """Test ticket registration handles database operation errors."""
    mock_user_repo.get_by_username.return_value = sample_user
    mock_ticket_repo.get_by_ticket_details.return_value = sample_ticket
    mock_ticket_repo.register_ticket.side_effect = DbOperationException("DB Error")

    with pytest.raises(AppValidationException, match="Error registering ticket"):
        await ticket_service.register_ticket(sample_user.username, sample_ticket)


async def test_register_ticket_registration_failed(
    ticket_service: TicketService,
    mock_user_repo: AsyncMock,
    mock_ticket_repo: AsyncMock,
    sample_user: User,
    sample_ticket: Ticket,
) -> None:
    """Test ticket registration fails when register_ticket returns False."""
    mock_user_repo.get_by_username.return_value = sample_user
    mock_ticket_repo.get_by_ticket_details.side_effect = [sample_ticket, None]
    mock_ticket_repo.register_ticket.return_value = False

    with pytest.raises(AppValidationException, match="Error registering ticket"):
        await ticket_service.register_ticket(sample_user.username, sample_ticket)


# ==================== Tests for log_attendance ====================


async def test_log_attendance_success(
    ticket_service: TicketService,
    mock_ticket_repo: AsyncMock,
    sample_registered_ticket: Ticket,
    sample_attendance_log: AttendanceLog,
) -> None:
    """Test successful attendance logging with valid TOTP code."""
    used_ticket = sample_registered_ticket.model_copy()
    used_ticket.status = "used"

    with patch("src.register_ticket_api.services.ticket_service.pyotp.TOTP") as mock_totp_class:
        mock_totp_instance = MagicMock()
        mock_totp_instance.verify.return_value = True
        mock_totp_class.return_value = mock_totp_instance

        mock_ticket_repo.get_by_ticket_details.side_effect = [sample_registered_ticket, used_ticket]
        mock_ticket_repo.mark_ticket_as_used.return_value = True

        result = await ticket_service.log_attendance(sample_attendance_log)

        assert result == used_ticket
        assert result.status == "used"
        # Verify TOTP was called with base32 encoded seed and correct interval
        call_args = mock_totp_class.call_args
        assert call_args[1]["interval"] == TicketService.TOTP_INTERVAL_SECONDS
        assert isinstance(call_args[0][0], str)  # Seed should be base32 string
        mock_totp_instance.verify.assert_called_once_with(
            sample_attendance_log.totp_code, valid_window=0
        )
        mock_ticket_repo.mark_ticket_as_used.assert_called_once_with(sample_registered_ticket.id)


async def test_log_attendance_ticket_not_found(
    ticket_service: TicketService,
    mock_ticket_repo: AsyncMock,
    sample_attendance_log: AttendanceLog,
) -> None:
    """Test attendance logging fails when ticket does not exist."""
    mock_ticket_repo.get_by_ticket_details.return_value = None

    with pytest.raises(AppValidationException, match="Ticket does not exist"):
        await ticket_service.log_attendance(sample_attendance_log)


async def test_log_attendance_ticket_no_id(
    ticket_service: TicketService,
    mock_ticket_repo: AsyncMock,
    sample_attendance_log: AttendanceLog,
) -> None:
    """Test attendance logging fails when ticket has no ID."""
    ticket_no_id = Ticket(
        id=None,
        seat=TEST_SEAT,
        gate=TEST_GATE,
        seed=VALID_SEED_BASE64,
        status="valid",
        created_at="2024-01-01T00:00:00Z",
        used_at=None,
        user_id=uuid4(),
    )
    mock_ticket_repo.get_by_ticket_details.return_value = ticket_no_id

    with pytest.raises(AppValidationException, match="Ticket has no ID"):
        await ticket_service.log_attendance(sample_attendance_log)


async def test_log_attendance_ticket_not_registered(
    ticket_service: TicketService,
    mock_ticket_repo: AsyncMock,
    sample_ticket: Ticket,
    sample_attendance_log: AttendanceLog,
) -> None:
    """Test attendance logging fails when ticket is not registered to a user."""
    mock_ticket_repo.get_by_ticket_details.return_value = sample_ticket

    with pytest.raises(AppValidationException, match="Ticket is not yet registered"):
        await ticket_service.log_attendance(sample_attendance_log)


async def test_log_attendance_ticket_no_seed(
    ticket_service: TicketService,
    mock_ticket_repo: AsyncMock,
    sample_attendance_log: AttendanceLog,
) -> None:
    """Test attendance logging fails when ticket has no seed."""
    ticket_no_seed = Ticket(
        id=uuid4(),
        seat=TEST_SEAT,
        gate=TEST_GATE,
        user_id=uuid4(),
        seed=None,
        status="valid",
        created_at="2024-01-01T00:00:00Z",
        used_at=None,
    )
    mock_ticket_repo.get_by_ticket_details.return_value = ticket_no_seed

    with pytest.raises(AppValidationException, match="Ticket has no seed"):
        await ticket_service.log_attendance(sample_attendance_log)


async def test_log_attendance_invalid_totp_code(
    ticket_service: TicketService,
    mock_ticket_repo: AsyncMock,
    sample_registered_ticket: Ticket,
    sample_attendance_log: AttendanceLog,
) -> None:
    """Test attendance logging fails with invalid TOTP code."""
    with patch("src.register_ticket_api.services.ticket_service.pyotp.TOTP") as mock_totp_class:
        mock_totp_instance = MagicMock()
        mock_totp_instance.verify.return_value = False
        mock_totp_class.return_value = mock_totp_instance

        mock_ticket_repo.get_by_ticket_details.return_value = sample_registered_ticket

        with pytest.raises(AppValidationException, match="Invalid TOTP ticket code"):
            await ticket_service.log_attendance(sample_attendance_log)

        mock_totp_instance.verify.assert_called_once_with(
            sample_attendance_log.totp_code, valid_window=0
        )


async def test_log_attendance_db_operation_exception(
    ticket_service: TicketService,
    mock_ticket_repo: AsyncMock,
    sample_registered_ticket: Ticket,
    sample_attendance_log: AttendanceLog,
) -> None:
    """Test attendance logging handles database operation errors."""
    with patch("src.register_ticket_api.services.ticket_service.pyotp.TOTP") as mock_totp_class:
        mock_totp_instance = MagicMock()
        mock_totp_instance.verify.return_value = True
        mock_totp_class.return_value = mock_totp_instance

        mock_ticket_repo.get_by_ticket_details.return_value = sample_registered_ticket
        mock_ticket_repo.mark_ticket_as_used.side_effect = DbOperationException("DB Error")

        with pytest.raises(AppValidationException, match="Error creating user"):
            await ticket_service.log_attendance(sample_attendance_log)


async def test_log_attendance_update_failed(
    ticket_service: TicketService,
    mock_ticket_repo: AsyncMock,
    sample_registered_ticket: Ticket,
    sample_attendance_log: AttendanceLog,
) -> None:
    """Test attendance logging fails when mark_ticket_as_used returns False."""
    with patch("src.register_ticket_api.services.ticket_service.pyotp.TOTP") as mock_totp_class:
        mock_totp_instance = MagicMock()
        mock_totp_instance.verify.return_value = True
        mock_totp_class.return_value = mock_totp_instance

        mock_ticket_repo.get_by_ticket_details.side_effect = [sample_registered_ticket, None]
        mock_ticket_repo.mark_ticket_as_used.return_value = False

        with pytest.raises(AppValidationException, match="Error updating ticket .* state"):
            await ticket_service.log_attendance(sample_attendance_log)


async def test_log_attendance_ticket_already_used(
    ticket_service: TicketService,
    mock_ticket_repo: AsyncMock,
    sample_registered_ticket: Ticket,
    sample_attendance_log: AttendanceLog,
) -> None:
    """Test attendance logging fails when ticket is already used."""
    used_ticket = sample_registered_ticket.model_copy()
    used_ticket.status = "used"
    mock_ticket_repo.get_by_ticket_details.return_value = used_ticket

    with pytest.raises(AppValidationException, match="Invalid ticket"):
        await ticket_service.log_attendance(sample_attendance_log)
