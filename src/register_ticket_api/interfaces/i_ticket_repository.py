from abc import ABC, abstractmethod
from uuid import UUID

from entities import Ticket, User


class ITicketRepository(ABC):
    @abstractmethod
    async def register_ticket(self, user: User, ticket: Ticket) -> bool:
        pass

    @abstractmethod
    async def get_by_ticket_details(self, seat: str, gate: str) -> Ticket | None:
        # TODO: In the long run this will fail due to the abscence of an event entity
        pass

    @abstractmethod
    async def mark_ticket_as_used(self, ticket_id: UUID) -> bool:
        pass
