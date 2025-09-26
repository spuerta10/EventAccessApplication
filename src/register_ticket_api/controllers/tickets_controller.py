from fastapi import APIRouter, HTTPException, status

from services import TicketService
from entities import Ticket, AttendanceLog

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
            response_model= Ticket,
            status_code=status.HTTP_202_ACCEPTED,
            summary= "Registers a ticket to a user"
        )
        self.router.add_api_route(
            "/attendance",
            self.log_attendance,
            methods=["POST"],
            response_model=Ticket,
            status_code=status.HTTP_202_ACCEPTED,
            summary= "Validates ticket via TOTP code"
        )

    async def register_ticket(self, username: str, ticket: Ticket):  # TODO: Change for user_id
        try:
            return await self.__ticket_service.register_ticket(username, ticket)
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal error: {str(err)}"
            ) from err

    async def log_attendance(self, attendance: AttendanceLog) -> Ticket:
        try:
            return await self.__ticket_service.log_attendance(attendance)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))