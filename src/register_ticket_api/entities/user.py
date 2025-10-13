from uuid import UUID

from pydantic import BaseModel


class User(BaseModel):
    id: UUID | None
    username: str
    password: str
