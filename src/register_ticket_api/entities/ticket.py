from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel

class Ticket(BaseModel):
    id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    seat: str
    gate: str
    seed: Optional[str] = None  # TODO: should be secretstr
    status: Literal["valid", "used", "revoked"] = "valid"
    created_at: Optional[datetime] = None
    used_at: Optional[datetime] = None