import requests
import os
from dotenv import load_dotenv

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
