from dataclasses import dataclass

from register_ticket_api.entities import User
from register_ticket_api.exceptions import DbOperationException
from register_ticket_api.infraestructure import PostgreSQLDbContext
from register_ticket_api.interfaces import IUserRepository


@dataclass
class UserRepository(IUserRepository):
    db_context: PostgreSQLDbContext

    async def get_by_username(self, username: str) -> User | None:
        DB_QUERY: str = """
        SELECT DISTINCT
            user_id as id,
            username,
            password_hash as password
        FROM users
        WHERE LOWER(username) = LOWER($1)
        """
        db_conn = await self.db_context.get_connection()
        row = await db_conn.fetchrow(DB_QUERY, username)
        if row:
            return User(**row)
        return None

    async def create_user(self, new_user: User) -> bool:
        SP_NAME: str = "sp_insert_user"
        created: bool = False
        try:
            db_conn = await self.db_context.get_connection()
            params: tuple = (
                new_user.username,  # p_username
                new_user.password,  # p_password
            )
            rows_affected: int = await db_conn.execute(f"CALL {SP_NAME}($1, $2)", *params)

            if rows_affected != 0:
                created = True
        except Exception as e:
            raise DbOperationException(e) from e

        return created
