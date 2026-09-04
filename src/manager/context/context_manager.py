from ...providerdata.context import ProviderContext
from ..memory.memory_manager import NovaMemoryManager
from ..conversation.conversation_manager import NovaConversationManager
from ..cache.cache_manager import NovaCacheManager


class NovaContextManager:
    def __init__(self):
        self.cache_manager = NovaCacheManager()
        self.memory_manager = NovaMemoryManager(
            self.cache_manager
        )
        self.conversations_manger = NovaConversationManager(
            self.cache_manager
        )

    def create_provider_context(
        self,
        message,
        userUID,
        chatUID,
    ):
        memories = self.memory_manager.get_context(userUID)
        conversation = self.conversations_manger.get_context(chatUID)

        return ProviderContext(
            message=message,
            userUID=userUID,
            chatUID=chatUID,
            memories=memories,
            conversation=conversation
        )
