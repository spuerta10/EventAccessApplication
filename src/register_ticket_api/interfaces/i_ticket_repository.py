from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from entities import User, Ticket

class ITicketRepository(ABC):
    
    @abstractmethod
    def register_ticket(self, user: User, ticket: Ticket) -> bool:
        pass

    @abstractmethod
    def get_by_ticket_details(self, seat: str, gate: str) -> Optional[Ticket]:
        # TODO: In the long run this will fail due to the abscence of an event entity
        pass

    @abstractmethod
    def mark_ticket_as_used(self, ticket_id: UUID) -> bool:
        pass