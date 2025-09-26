import os

from dotenv import load_dotenv
import asyncpg

load_dotenv()  # load env variables from .env file

class PostgreSQLDbContext:
    def __parse_env_vars(self) -> dict:
        return {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT')),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'db': os.getenv('DB_NAME'),
        }
    
    async def get_connection(self) -> asyncpg.Connection:
        conn_params: dict = self.__parse_env_vars()
        return await asyncpg.connect(**conn_params)