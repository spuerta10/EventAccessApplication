from dataclasses import dataclass
from typing import Any
from uuid import UUID

from register_ticket_api.entities import Ticket, User
from register_ticket_api.exceptions import DbOperationException
from register_ticket_api.infraestructure import PostgreSQLDbContext
from register_ticket_api.interfaces import ITicketRepository


@dataclass
class TicketRepository(ITicketRepository):
    db_context: PostgreSQLDbContext

    async def register_ticket(self, user: User, ticket: Ticket) -> bool:
        SP_NAME: str = "sp_register_ticket_to_user"
        registered: bool = False
        try:
            db_conn = await self.db_context.get_connection()
            params: tuple = (
                ticket.id,  # p_ticket_id
                user.id,  # p_user_id
            )
            rows_affected = await db_conn.execute(f"CALL {SP_NAME}($1, $2)", *params)
            if rows_affected != 0:
                registered = True
        except Exception as e:
            raise DbOperationException(e) from e
        return registered

    async def get_by_ticket_details(self, seat: str, gate: str) -> Ticket | None:
        DB_QUERY: str = """
        SELECT
            t.ticket_id AS id,
            t.user_id,
            t.seat,
            t.gate,
            encode(t.seed, 'base64') AS seed,
            t.status,
            t.created_at,
            t.used_at
        FROM tickets t
        WHERE t.seat = $1
            AND t.gate = $2
            AND t.status != 'revoked';
        """
        try:
            db_conn = await self.db_context.get_connection()
            row = await db_conn.fetchrow(DB_QUERY, seat, gate)
        except Exception as e:
            raise DbOperationException(e) from e
        if row:
            return Ticket(**row)
        return None

    async def mark_ticket_as_used(self, ticket_id: UUID) -> Any:  # bool
        FN_NAME: str = "fn_mark_ticket_as_used"
        try:
            db_conn = await self.db_context.get_connection()
            rows_affected = await db_conn.fetchval(f"SELECT {FN_NAME}($1)", ticket_id)
        except Exception as e:
            raise DbOperationException(e) from e
        else:
            return rows_affected
