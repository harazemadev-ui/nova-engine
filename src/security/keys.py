import os
from dotenv import load_dotenv


load_dotenv()


class OldNovaKey:

    def __init__(self):

        self.api_key = os.getenv(
            "NOVA_API_KEY"
        )

        print(
            "NOVA key loaded:",
            bool(self.api_key)
        )

        if not self.api_key:
            raise RuntimeError(
                "NOVA_API_KEY missing"
            )

    def verify_api_key(self, api_key: str):

        return api_key == self.api_key
