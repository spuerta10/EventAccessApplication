from abc import ABC, abstractmethod
from collections.abc import Awaitable
from uuid import UUID

from entities import Ticket, User


class ITicketRepository(ABC):
    @abstractmethod
    async def register_ticket(self, user: User, ticket: Ticket) -> Awaitable[bool]:
        pass

    @abstractmethod
    async def get_by_ticket_details(self, seat: str, gate: str) -> Awaitable[Ticket | None]:
        # TODO: In the long run this will fail due to the abscence of an event entity
        pass

    @abstractmethod
    async def mark_ticket_as_used(self, ticket_id: UUID) -> Awaitable[bool]:
        pass
