from base64 import b32encode, b64decode
from dataclasses import dataclass
from typing import ClassVar

import pyotp
from entities import AttendanceLog, Ticket, User
from exceptions import AppValidationException, DbOperationException
from interfaces import ITicketRepository, IUserRepository
from loguru import logger


@dataclass
class TicketService:
    user_repo: IUserRepository
    ticket_repo: ITicketRepository

    TOTP_INTERVAL_SECONDS: ClassVar[int] = 60

    async def register_ticket(self, username: str, ticket: Ticket) -> Ticket:
        logger.info(
            f"Attempting to register ticket "
            f"seat={ticket.seat}, gate={ticket.gate} "
            f"for user={username}"
        )
        existent_user: User | None = await self.user_repo.get_by_username(username)
        if not existent_user:
            logger.warning(f"Registration failed: user {username} does not exists")
            raise AppValidationException(f"User {username} does not exist.")

        valid_ticket_details, err_msg = self.__is_valid_ticket_details(ticket)
        if not valid_ticket_details:
            logger.warning(
                f"Registration failed: invalid ticket details for "
                f"seat={ticket.seat}, gate={ticket.gate} -> {err_msg}"
            )
            raise AppValidationException(f"Invalid ticket details: {err_msg}")

        existent_ticket: Ticket | None = await self.ticket_repo.get_by_ticket_details(
            seat=ticket.seat, gate=ticket.gate
        )
        if not existent_ticket:
            logger.warning(
                f"Registration failed: ticket "
                f"seat={ticket.seat}, gate={ticket.gate} "
                "does not exist in DB"
            )
            raise AppValidationException("Ticket does not exist")

        if existent_ticket.user_id is not None:
            logger.info(
                f"Registration rejected: ticket {existent_ticket.id} "
                f"is already registered to user {existent_ticket.user_id}"
            )
            raise AppValidationException("Ticket is already registered")

        try:
            registered: bool = await self.ticket_repo.register_ticket(
                existent_user, existent_ticket
            )
            registered_ticket: Ticket | None = await self.ticket_repo.get_by_ticket_details(
                seat=ticket.seat, gate=ticket.gate
            )
            if not registered or not registered_ticket:
                raise AppValidationException("Error registering ticket.")
            logger.info(
                f"Ticket {existent_ticket.id} successfully registered for user={username}, "
                f"seed={existent_ticket.seed}"
            )
        except DbOperationException as err:
            logger.exception(
                f"Database error while registering ticket "
                f"seat={ticket.seat}, gate={ticket.gate} -> {err}"
            )
            raise AppValidationException(f"Error registering ticket: {err}") from err
        return registered_ticket

    async def log_attendance(self, attendance: AttendanceLog) -> Ticket:
        logger.info(
            f"Attendance attempt: seat={attendance.seat}, "
            f"gate={attendance.gate}, totp={attendance.totp_code}"
        )
        existent_ticket: Ticket | None = await self.ticket_repo.get_by_ticket_details(
            seat=attendance.seat, gate=attendance.gate
        )
        if not existent_ticket:
            logger.warning(
                f"Attendance failed: no ticket found for "
                f"seat={attendance.seat}, gate={attendance.gate}"
            )
            raise AppValidationException("Ticket does not exist")
        elif not existent_ticket.id:
            logger.warning(
                f"Attendance failed: ticket has no ID for "
                f"seat={attendance.seat}, gate={attendance.gate}"
            )
            raise AppValidationException("Ticket has no ID")
        elif existent_ticket.user_id is None:
            logger.warning(
                f"Attendance failed: ticket {existent_ticket.id} is not registered to a user"
            )
            raise AppValidationException("Ticket is not yet registered")
        elif existent_ticket.status != "valid":
            logger.warning(
                f"Attendance failed: ticket {existent_ticket.id} "
                f"has invalid status={existent_ticket.status}"
            )
            raise AppValidationException("Invalid ticket")
        elif existent_ticket.seed is None:
            logger.error(f"Attendance failed: ticket {existent_ticket.id} has no seed")
            raise AppValidationException("Ticket has no seed")

        seed_bytes: bytes = b64decode(existent_ticket.seed)
        seed_base32: str = b32encode(seed_bytes).decode("utf-8")
        totp = pyotp.TOTP(
            seed_base32, interval=self.TOTP_INTERVAL_SECONDS
        )  # after specified seconds token expires
        if not totp.verify(attendance.totp_code, valid_window=0):
            logger.warning(
                f"Attendance rejected: invalid TOTP code={attendance.totp_code} "
                f"for ticket {existent_ticket.id} "
                "(possible fraud attempt)"
            )
            raise AppValidationException("Invalid TOTP ticket code.")

        try:
            updated: bool = await self.ticket_repo.mark_ticket_as_used(existent_ticket.id)
            updated_ticket: Ticket | None = await self.ticket_repo.get_by_ticket_details(
                seat=attendance.seat, gate=attendance.gate
            )
            if not updated or not updated_ticket:
                raise AppValidationException(f"Error updating ticket {existent_ticket.id} state")
            logger.info(
                f"Attendance success: ticket {updated_ticket.id} "
                f"marked as used for user {updated_ticket.user_id}"
            )
        except DbOperationException as err:
            logger.exception(
                f"Database error while marking attendance for ticket {existent_ticket.id}: {err}"
            )
            raise AppValidationException(f"Error creating user: {err}") from err
        return updated_ticket

    def __is_valid_ticket_details(self, ticket: Ticket) -> tuple[bool, str]:
        # TODO: Here event validation logic
        return (True, "")
