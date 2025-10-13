import re
from dataclasses import dataclass

from entities import User
from exceptions import AppValidationException, DbOperationException
from interfaces import IUserRepository


@dataclass
class UserService:
    user_repo: IUserRepository

    async def create_user(self, new_user: User) -> User:
        valid_user_details, err_msg = self.__is_valid_user_details(new_user)
        if not valid_user_details:
            raise AppValidationException(f"Invalid user details: {err_msg}")

        existent_user: User | None = await self.user_repo.get_by_username(new_user.username)
        if existent_user:
            raise AppValidationException("Can't create taken username")

        try:
            created: bool = await self.user_repo.create_user(new_user)
            created_user: User | None = await self.user_repo.get_by_username(new_user.username)
            if not created or not created_user:
                raise AppValidationException("Error creating user.")
        except DbOperationException as err:
            raise AppValidationException(f"Error creating user: {err}") from err
        return created_user

    def __is_valid_user_details(self, user: User) -> tuple[bool, str]:
        USERNAME_PATTERN: str = (
            r"^[A-Za-z0-9_-]{3,10}$"  # letras, números, guion y guion bajo. De 3 a 10 caracteres
        )
        MIN_PASWORD_LENGTH: int = 8
        # al menos 8 caracteres, una mayúscula, una minúscula, un dígito y un caracter especial
        PASSWORD_PATTERN: str = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_\-])[A-Za-z\d@$!%*?&_\-]{8,}$"  # noqa: S105
        )
        is_valid, msg = True, "✅ Usuario y contraseña válidos."
        if not user.username:
            is_valid, msg = False, "Missing username."
        if not user.password:
            is_valid, msg = False, "Missing password."
        if not re.match(USERNAME_PATTERN, user.username):
            return (
                False,
                (
                    "❌ El nombre de usuario solo puede contener letras, números, "
                    "guiones (-, _) y tener entre 3 y 20 caracteres."
                ),
            )
        if not re.match(PASSWORD_PATTERN, user.password):
            if len(user.password) < MIN_PASWORD_LENGTH:
                is_valid, msg = False, "❌ La contraseña debe tener al menos 8 caracteres."
            elif not re.search(r"[a-z]", user.password):
                is_valid, msg = False, "❌ La contraseña debe incluir al menos una letra minúscula."
            elif not re.search(r"[A-Z]", user.password):
                is_valid, msg = False, "❌ La contraseña debe incluir al menos una letra mayúscula."
            elif not re.search(r"\d", user.password):
                is_valid, msg = False, "❌ La contraseña debe incluir al menos un número."
            elif not re.search(r"[@$!%*?&_\-]", user.password):
                is_valid, msg = (
                    False,
                    "❌ La contraseña debe incluir al menos un carácter especial (@$!%*?&_-).",
                )
            is_valid, msg = False, "❌ La contraseña no cumple con los requisitos de seguridad."
        return (is_valid, msg)
