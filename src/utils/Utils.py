import requests
import os
from dotenv import load_dotenv
import secrets
import string

load_dotenv()


class NovaUtils:

    def apiPassage(self, method: str, url: str, body: dict | None = None):

        method = method.upper()

        response = requests.request(
            method,
            url,
            json=body,
            timeout=10
        )

        return response

    def gen_nova_api_key(self):
        # Prefix
        prefixes = [
            "NOV",
            "SAP",
            "NOV-SAP"
        ]

        prefix = secrets.choice(prefixes)

        # Random body
        body = _generate_body(164)

        # Suffix
        suffixes = [
            "-SF",
            "-HZ",
            "-NV"
        ]

        suffix = secrets.choice(
            suffixes
        )

        return (
            f"{prefix}-{body}{suffix}"
        )


def _generate_body(length: int = 64) -> str:

    characters = (
        string.ascii_letters +
        string.digits
    )

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )
