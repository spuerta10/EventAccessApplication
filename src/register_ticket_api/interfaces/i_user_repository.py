from abc import ABC, abstractmethod
from typing import Optional

from entities import User

class IUserRepository(ABC):
    @abstractmethod
    def create_user(self, new_user: User) -> bool:
        pass

    def get_by_username(self, username: str) -> Optional[User]:
        pass