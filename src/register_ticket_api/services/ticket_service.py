from dataclasses import dataclass
from typing import Optional, ClassVar
from base64 import b64decode, b32encode

import pyotp

from interfaces import IUserRepository, ITicketRepository
from entities import User, Ticket, AttendanceLog
from exceptions import AppValidationException, DbOperationException

@dataclass
class TicketService:
    user_repo: IUserRepository
    ticket_repo: ITicketRepository

    TOTP_INTERVAL_SECONDS: ClassVar[int] = 60

    async def register_ticket(self, username: str, ticket: Ticket) -> Ticket:
        existent_user: Optional[User] = await self.user_repo.get_by_username(username)
        if not existent_user:
            raise AppValidationException(f"User {username} does not exist.")
        
        valid_ticket_details, err_msg = self.__is_valid_ticket_details(ticket)
        if not valid_ticket_details:
            raise AppValidationException(f"Invalid ticket details: {err_msg}")
        
        existent_ticket: Optional[Ticket] = await self.ticket_repo.get_by_ticket_details(
            seat=ticket.seat,
            gate=ticket.gate
        )
        if not existent_ticket:
            raise AppValidationException("Ticket does not exist")
        
        if existent_ticket.user_id is not None:
            raise AppValidationException(f"Ticket is already registered")
        
        try:
            registered: bool = await self.ticket_repo.register_ticket(existent_user, existent_ticket)
            if not registered:
                raise AppValidationException("Error registering ticket.")
            registered_ticket: Optional[Ticket] = await self.ticket_repo.get_by_ticket_details(
                seat=ticket.seat,
                gate=ticket.gate
            )
        except DbOperationException as err:
            raise AppValidationException(f"Error registering ticket: {err}") from err
        return registered_ticket
        
    
    async def log_attendance(self, attendance: AttendanceLog) -> Ticket:
        existent_ticket: Optional[Ticket] = await self.ticket_repo.get_by_ticket_details(
            seat=attendance.seat,
            gate=attendance.gate
        )
        if not existent_ticket:
            raise AppValidationException("Ticket does not exist")
        elif (existent_ticket.user_id is None):
            raise AppValidationException(f"Ticket is not yet registered")
        elif existent_ticket.status is not "valid":
            raise AppValidationException("Invalid ticket")
        
        seed_bytes: bytes = b64decode(existent_ticket.seed)
        seed_base32: str = b32encode(seed_bytes).decode("utf-8")
        totp = pyotp.TOTP(seed_base32, interval=self.TOTP_INTERVAL_SECONDS)  # after specified seconds token expires
        if not totp.verify(attendance.totp_code, valid_window=1):
            raise AppValidationException("Invalid TOTP ticket code.")  # this could be a fraud
        
        try:
            updated: bool = await self.ticket_repo.mark_ticket_as_used(existent_ticket.id)
            if not updated:
                raise AppValidationException(f"Error updating ticket {existent_ticket.id} state")
            updated_ticket: Optional[Ticket] = await self.ticket_repo.get_by_ticket_details(
                seat=attendance.seat,
                gate=attendance.gate
            )
        except DbOperationException as err:
            raise AppValidationException(f"Error creating user: {err}") from err
        return updated_ticket
        

    def __is_valid_ticket_details(self, ticket: Ticket) -> tuple[bool, str]:
        # TODO: Here event validation logic
        return (True, "")