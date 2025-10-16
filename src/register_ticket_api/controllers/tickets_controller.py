from fastapi import APIRouter, HTTPException, status
from loguru import logger

from register_ticket_api.entities import AttendanceLog, Ticket
from register_ticket_api.exceptions import AppValidationException
from register_ticket_api.services import TicketService


class TicketsController:
    def __init__(self, ticket_service: TicketService):
        self.__ticket_service = ticket_service
        self.router = APIRouter(prefix="/api/users")
        self.__setup_routes()

    def __setup_routes(self) -> None:
        self.router.add_api_route(
            "/{username}/tickets",
            self.register_ticket,
            methods=["POST"],
            response_model=Ticket,
            status_code=status.HTTP_202_ACCEPTED,
            summary="Registers a ticket to a user",
        )
        self.router.add_api_route(
            "/attendance",
            self.log_attendance,
            methods=["POST"],
            response_model=Ticket,
            status_code=status.HTTP_202_ACCEPTED,
            summary="Validates ticket via TOTP code",
        )

    async def register_ticket(
        self, username: str, ticket: Ticket
    ) -> Ticket:  # TODO: Change for user_id
        logger.info(
            f"Request received at /tickets for username={username}, "
            f"seat={ticket.seat}, gate={ticket.gate}"
        )
        try:
            return await self.__ticket_service.register_ticket(username, ticket)
        except AppValidationException as err:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)) from err
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal error: {err!s}",
            ) from err

    async def log_attendance(self, attendance: AttendanceLog) -> Ticket:
        logger.info(
            f"Request received at /tickets for seat={attendance.seat}, "
            f"gate={attendance.gate}, totp={attendance.totp_code}"
        )
        try:
            return await self.__ticket_service.log_attendance(attendance)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
