from fastapi import APIRouter, HTTPException, status

from services import UserService
from entities import User

class UsersController:
    def __init__(self, user_service: UserService):
        self.__user_service = user_service
        self.router = APIRouter(prefix="/api/users")
        self.__setup_routes()
    
    def __setup_routes() -> None:
        ...

    async def create_user(self, user: User):
        try:
            self.__user_service.create_user(user)
        except Exception as err:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal error: {str(err)}"
            ) from err