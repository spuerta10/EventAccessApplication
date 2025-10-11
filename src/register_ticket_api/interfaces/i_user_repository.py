from abc import ABC, abstractmethod
from collections.abc import Awaitable

from entities import User


class IUserRepository(ABC):
    @abstractmethod
    async def create_user(self, new_user: User) -> Awaitable[bool]:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Awaitable[User | None]:
        pass
