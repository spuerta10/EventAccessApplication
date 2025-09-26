from typing import Optional
from dataclasses import dataclass
import re

from interfaces import IUserRepository
from entities import User
from exceptions import AppValidationException, DbOperationException

@dataclass
class UserService:
    user_repo: IUserRepository

    async def create_user(self, new_user: User):
        valid_user_details, err_msg = self.__is_valid_user_details(new_user)
        if not valid_user_details:
            raise AppValidationException(f"Invalid user details: {err_msg}")

        existent_user: Optional[User] = await self.user_repo.get_by_username(new_user.username)
        if existent_user:
            raise AppValidationException("Can't create taken username") 
        
        try:
            created: bool = await self.user_repo.create_user(new_user)
            if not created:
                raise AppValidationException("Error creating user.")
            created_user: Optional[User] = await self.user_repo.get_by_username(new_user.username)
        except DbOperationException as err:
            raise AppValidationException(f"Error creating user: {err}") from err
        return created_user

    def __is_valid_user_details(self, user: User) -> tuple[bool, str]:
        USERNAME_PATTERN: str = r'^[A-Za-z0-9_-]{3,10}$'  # letras, números, guion y guion bajo. De 3 a 10 caracteres
        # al menos 8 caracteres, una mayúscula, una minúscula, un dígito y un caracter especial
        PASSWORD_PATTERN: str = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_\-])[A-Za-z\d@$!%*?&_\-]{8,}$'
        if not user.username:
            return (False, "Missing username.")
        if not user.password:
            return (False, "Missing password.")
        if not re.match(USERNAME_PATTERN, user.username):
            return (False, "❌ El nombre de usuario solo puede contener letras, números, guiones (-, _) y tener entre 3 y 20 caracteres.")
        if not re.match(PASSWORD_PATTERN, user.password):
            if len(user.password) < 8:
                return (False, "❌ La contraseña debe tener al menos 8 caracteres.")
            if not re.search(r'[a-z]', user.password):
                return (False, "❌ La contraseña debe incluir al menos una letra minúscula.")
            if not re.search(r'[A-Z]', user.password):
                return (False, "❌ La contraseña debe incluir al menos una letra mayúscula.")
            if not re.search(r'\d', user.password):
                return (False, "❌ La contraseña debe incluir al menos un número.")
            if not re.search(r'[@$!%*?&_\-]', user.password):
                return (False, "❌ La contraseña debe incluir al menos un carácter especial (@$!%*?&_-).")
            return (False, "❌ La contraseña no cumple con los requisitos de seguridad.")
        return (True, "✅ Usuario y contraseña válidos.")
        