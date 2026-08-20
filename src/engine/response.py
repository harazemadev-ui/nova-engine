class NovaResponse:

    def __init__(self, response: str | None = None):
        self.response = response

    def to_dict(self):
        return {
            "response": self.response
        }
