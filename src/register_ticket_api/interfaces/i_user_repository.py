from abc import ABC, abstractmethod

from register_ticket_api.entities import User


class IUserRepository(ABC):
    @abstractmethod
    async def create_user(self, new_user: User) -> bool:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> User | None:
        pass
