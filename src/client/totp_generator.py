from argparse import ArgumentParser
from base64 import b32encode, b64decode
from typing import ClassVar

from pyotp import TOTP


class TOTPGenerator:
    TOTP_INTERVAL_SECONDS: ClassVar[int] = 60

    def __init__(self, seed_base64: str) -> None:
        if not seed_base64:
            raise ValueError("Seed cannot be empty")
        bytes_seed: bytes = b64decode(seed_base64)
        seed_base32 = b32encode(bytes_seed).decode("utf-8")
        self.__totp = TOTP(seed_base32, interval=self.TOTP_INTERVAL_SECONDS)

    def generate_code(self) -> str:
        return str(self.__totp.now())


if __name__ == "__main__":  # pragma: no cover
    parser = ArgumentParser(description="Genera un código TOTP desde una semilla hexadecimal")
    parser.add_argument("seed", type=str, help="Seed en hexadecimal (sin 0x)")
    args = parser.parse_args()

    totp = TOTPGenerator(args.seed)
    code: str = totp.generate_code()
    print(f"Your TOTP code is: {code}")
