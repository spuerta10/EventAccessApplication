from entities import User
from fastapi import APIRouter, HTTPException, status
from services import UserService


class UsersController:
    def __init__(self, user_service: UserService) -> None:
        self.__user_service = user_service
        self.router = APIRouter(prefix="/api/users")
        self.__setup_routes()

    def __setup_routes(self) -> None: ...

    async def create_user(self, user: User) -> User:
        try:
            return await self.__user_service.create_user(user)
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal error: {err!s}",
            ) from err
