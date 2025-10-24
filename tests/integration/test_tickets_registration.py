"""
Integration tests for the ticket registration API and database flow.
"""

from typing import Any

import requests
from psycopg2._psycopg import connection

OK_STATUS_CODE: int = 202
ERROR_STATUS_CODE: int = 400
REQUEST_TIMEOUT: int = 10  # seconds


def test_register_ticket_flow(
    base_url: str, db_connection: connection, test_username: str = "spuertaf"
) -> None:
    """
    Test the full ticket registration flow for a user.

    Sends a POST request to register a ticket for the specified user, then
    verifies that the ticket is correctly stored in the database with
    expected values.

    Args:
        base_url (str): Base URL of the ticket registration API.
        db_connection (connection): Active PostgreSQL database connection.
        test_username (str, optional): Username for which the ticket is registered.
            Defaults to "spuertaf".
    """
    headers: dict[str, str] = {"Content-Type": "application/json"}
    payload: dict[str, str] = {"seat": "A12", "gate": "G1"}
    endpoint: str = f"/api/users/{test_username}/tickets"

    response = requests.post(
        url=base_url + endpoint, headers=headers, json=payload, timeout=REQUEST_TIMEOUT
    )

    assert response.status_code == OK_STATUS_CODE

    ticket_id: str = response.json().get("id")
    assert ticket_id is not None

    response_user_id: str = response.json().get("user_id")
    assert response_user_id is not None

    used_at = response.json().get("used_at")
    assert used_at is None

    # see if database registered the ticket
    with db_connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                seat, gate, user_id, status
            FROM tickets
            WHERE
                ticket_id = %s
            """,
            (ticket_id,),
        )
        result: tuple[Any, Any, Any, Any] = cursor.fetchone()

    assert result is not None
    seat, gate, user_id, status = result
    assert seat == payload["seat"]
    assert gate == payload["gate"]
    assert str(user_id) == str(response_user_id)
    assert status == "valid"


def test_register_ticket_fails_when_already_registered(
    base_url: str,
    test_username: str = "juanperez",  # different user so tests don't collide
) -> None:
    """
    Test that registering the same ticket twice fails.

    Sends a POST request to register a ticket for the user, then attempts
    to register the same ticket again and expects an error.

    Args:
        base_url (str): Base URL of the ticket registration API.
        test_username (str, optional): Username for which the ticket is registered.
            Defaults to "juanperez".
    """
    headers: dict[str, str] = {"Content-Type": "application/json"}
    payload: dict[str, str] = {
        "seat": "B05",
        "gate": "G2",
    }  # different ticket info so tests don't collide
    endpoint: str = f"/api/users/{test_username}/tickets"

    first_response = requests.post(
        url=base_url + endpoint, headers=headers, json=payload, timeout=REQUEST_TIMEOUT
    )
    assert first_response.status_code == OK_STATUS_CODE

    second_response = requests.post(
        url=base_url + endpoint, headers=headers, json=payload, timeout=REQUEST_TIMEOUT
    )
    assert second_response.status_code == ERROR_STATUS_CODE


def test_invalid_ticket_registration_error(base_url: str, test_username: str = "spuertaf") -> None:
    """
    Test that registering a ticket with invalid data returns an error.

    Sends a POST request with invalid seat/gate values and expects the API
    to return an error code.

    Args:
        base_url (str): Base URL of the ticket registration API.
        test_username (str, optional): Username for which the ticket is registered.
            Defaults to "spuertaf".
    """
    headers: dict[str, str] = {"Content-Type": "application/json"}
    payload: dict[str, str] = {"seat": "B05", "gate": "G12"}
    endpoint: str = f"/api/users/{test_username}/tickets"

    response = requests.post(
        url=base_url + endpoint, headers=headers, json=payload, timeout=REQUEST_TIMEOUT
    )
    assert response.status_code == ERROR_STATUS_CODE
