class ProviderResult:

    def __init__(
        self,
        response: str,
        memory_actions: list[dict] | None = None
    ):
        self.response = response
        self.memory_actions = memory_actions or []
