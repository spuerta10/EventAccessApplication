from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel


class Ticket(BaseModel):
    id: UUID | None = None
    user_id: UUID | None = None
    seat: str
    gate: str
    seed: str | None = None  # TODO: should be secretstr
    status: Literal["valid", "used", "revoked"] = "valid"
    created_at: datetime | None = None
    used_at: datetime | None = None
