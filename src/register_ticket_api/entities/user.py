from uuid import UUID

from pydantic import BaseModel, SecretStr


class User(BaseModel):
    id: UUID | None
    username: str
    password: SecretStr | None
