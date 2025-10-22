import os
from collections.abc import Generator

import psycopg2
import pytest
from psycopg2._psycopg import connection


@pytest.fixture(scope="session")
def db_connection() -> Generator:
    conn: connection = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "event_access"),
        user=os.getenv("DB_USER", "test"),
        password=os.getenv("DB_PASSWORD", "TEST"),
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", "5432"),
    )
    yield conn
    conn.close()


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("BASE_URL", "http://localhost:8000")
