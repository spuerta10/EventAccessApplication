from typing import Optional
from uuid import UUID

from pydantic import BaseModel, SecretStr

class User(BaseModel):
    id: Optional[UUID]
    username: str
    password: Optional[SecretStr]