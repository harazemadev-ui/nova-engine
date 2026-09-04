class ProviderContext:

    def __init__(
        self,
        message,
        userUID,
        chatUID,
        memories,
        conversation
    ):
        self.message = message
        self.userUID = userUID
        self.chatUID = chatUID
        self.memories = memories
        self.conversation = conversation
