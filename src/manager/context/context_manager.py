from ...providerdata.context import ProviderContext

from ..memory.memory_manager import NovaMemoryManager
from ..conversation.conversation_manager import NovaConversationManager
from ..cache.cache_manager import NovaCacheManager
from ..token.token_budget_manager import NovaTokenBudgetManager
from ...errors.nova_error import NovaError
from ...errors.error_codes import ErrorCode

# ============================================================
# NOVA CONTEXT MANAGER
# ============================================================


class NovaContextManager:

    def __init__(self):

        # ====================================================
        # CACHE MANAGER
        # ====================================================

        self.cache_manager = NovaCacheManager()

        # ====================================================
        # MEMORY MANAGER
        # ====================================================

        self.memory_manager = NovaMemoryManager(
            self.cache_manager
        )

        # ====================================================
        # CONVERSATION MANAGER
        # ====================================================

        self.conversations_manager = NovaConversationManager(
            self.cache_manager
        )

        # ====================================================
        # TOKEN BUDGET MANAGER
        # ====================================================

        self.token_manager = NovaTokenBudgetManager()

    # ========================================================
    # CREATE PROVIDER CONTEXT
    # ========================================================

    def create_provider_context(
        self,
        message,
        userUID,
        chatUID,
        provider: str = "lumialit"
    ):

        # ====================================================
        # GET MEMORIES
        # ====================================================

        memories = self.memory_manager.get_context(
            userUID,
            chatUID
        )

        # ====================================================
        # GET CONVERSATION
        # ====================================================

        conversation = (
            self.conversations_manager.get_context(
                chatUID
            )
        )

        # ====================================================
        # CREATE INITIAL CONTEXT
        # ====================================================

        context = ProviderContext(
            message=message,
            userUID=userUID,
            chatUID=chatUID,
            memories=memories,
            conversation=conversation
        )

        # ====================================================
        # CHECK TOKEN BUDGET
        # ====================================================

        fits_budget = self.token_manager.check_tokens(
            provider,
            context
        )

        # ====================================================
        # CONTEXT ALREADY FITS
        # ====================================================

        if fits_budget:

            return context

        # ====================================================
        # TRIM CONVERSATION
        # ====================================================

        trimmed_messages = (
            self.token_manager.trim_context(
                conversation=conversation,
                memories=memories,
                provider=provider,
                current_message=message
            )
        )

        # ====================================================
        # UPDATE CONVERSATION
        # ====================================================

        conversation = {
            "messages": trimmed_messages
        }

        # ====================================================
        # CREATE NEW CONTEXT
        # ====================================================

        trimmed_context = ProviderContext(
            message=message,
            userUID=userUID,
            chatUID=chatUID,
            memories=memories,
            conversation=conversation
        )

        # ====================================================
        # CHECK AGAIN
        # ====================================================

        fits_budget = self.token_manager.check_tokens(
            provider,
            trimmed_context
        )

        # ====================================================
        # CONTEXT NOW FITS
        # ====================================================

        if fits_budget:

            return trimmed_context

        # ====================================================
        # CONVERSATION WAS REMOVED BUT CONTEXT IS STILL LARGE
        #
        # This means memories are likely consuming too much
        # of the provider budget.
        # ====================================================

        print(
            "WARNING: Conversation was trimmed but "
            "the context is still too large."
        )

        # ====================================================
        # REMOVE MEMORIES FOR THIS REQUEST
        #
        # Important:
        #
        # This does NOT delete memories from the database.
        #
        # It only prevents them from being sent to the AI.
        # ====================================================

        memories = {
            "user": [],
            "chat": []
        }

        # ====================================================
        # CREATE CONTEXT WITHOUT MEMORIES
        # ====================================================

        memory_trimmed_context = ProviderContext(
            message=message,
            userUID=userUID,
            chatUID=chatUID,
            memories=memories,
            conversation=conversation
        )

        # ====================================================
        # CHECK AGAIN
        # ====================================================

        fits_budget = self.token_manager.check_tokens(
            provider,
            memory_trimmed_context
        )

        # ====================================================
        # CONTEXT FITS WITHOUT MEMORIES
        # ====================================================

        if fits_budget:

            print(
                "WARNING: Memories were excluded from "
                "this request because they were too large."
            )

            return memory_trimmed_context

        # ====================================================
        # ONLY THE CURRENT MESSAGE REMAINS
        #
        # If this still does not fit, the user's message itself
        # is too large.
        # ====================================================

        raise NovaError(
            code=ErrorCode.MESSAGE_TOO_LARGE,
            message="The current message exceeds the provider token budget",
            source="context_manager.py",
            status_code=404,
        )
