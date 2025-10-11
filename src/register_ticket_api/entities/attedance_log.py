from pydantic import BaseModel


class AttendanceLog(BaseModel):
    # TODO: could also be ticketID
    seat: str
    gate: str
    totp_code: str
