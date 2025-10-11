from abc import ABC, abstractmethod

from entities import User


class IUserRepository(ABC):
    @abstractmethod
    def create_user(self, new_user: User) -> bool:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        pass
