from base64 import b64encode
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from pyotp import TOTP

from src.client.totp_generator import TOTPGenerator

VALID_SEED_BYTES: bytes = b"test_secret_key_"
VALID_SEED_BASE64: str = b64encode(VALID_SEED_BYTES).decode("utf-8")
INVALID_BASE_64_SEED: str = "invalid!@#$"
EXPECTED_CODE_LENGTH: int = 6


@pytest.fixture
def totp_generator() -> TOTPGenerator:
    return TOTPGenerator(seed_base64=VALID_SEED_BASE64)


@pytest.fixture
def base_time() -> datetime:
    """Fixed base time for tests."""
    return datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def test_init_with_valid_base64() -> None:
    """Test TOTPGenerator initialization with valid seed."""
    gen = TOTPGenerator(seed_base64=VALID_SEED_BASE64)

    assert gen._TOTPGenerator__totp is not None  # type: ignore[attr-defined]
    assert isinstance(gen._TOTPGenerator__totp, TOTP)  # type: ignore[attr-defined]


def test_init_with_invalid_base64() -> None:
    """Test TOTPGenerator initialization with invalid base64 seed raises exception."""
    with pytest.raises(ValueError):  # b64decode raises binascii.Error
        TOTPGenerator(seed_base64=INVALID_BASE_64_SEED)


def test_empty_seed_raises_error() -> None:
    """Test that empty seed raises an error."""
    with pytest.raises(ValueError):
        TOTPGenerator(seed_base64="")


def test_generate_code_returns_string(totp_generator: TOTPGenerator) -> None:
    """Test that generate_code returns a string."""
    code: str = totp_generator.generate_code()

    assert isinstance(code, str)
    assert len(code) == EXPECTED_CODE_LENGTH
    assert code.isdigit()


def test_generate_code_changes_over_time(
    base_time: datetime, totp_generator: TOTPGenerator
) -> None:
    """Test that code changes at the exact interval boundary."""
    with patch("pyotp.totp.datetime") as mock_time:
        from datetime import timedelta

        # first code at time 0
        mock_time.datetime.now.return_value = base_time
        code1 = totp_generator.generate_code()

        # second code at t=TOTP_INTERVAL_SECONDS
        mock_time.datetime.now.return_value = base_time + timedelta(
            seconds=totp_generator.TOTP_INTERVAL_SECONDS
        )
        code2 = totp_generator.generate_code()

        assert code1 != code2
