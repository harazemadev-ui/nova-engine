from ...providerdata.context import ProviderContext
from ...errors.nova_error import NovaError
from ...errors.error_codes import ErrorCode


class NovaTokenBudgetManager:

    def __init__(self):

        self.PROVIDER_LIMITS = {

            "lumialit": {
                "context_window": 131072,
                "budget": 6500,
            },

            "openrouter": {
                "context_window": 1048576,
                "budget": 32000,
            }

        }

    # ==========================================
    # TRIM CONTEXT
    # ==========================================

    def trim_context(
        self,
        conversation,
        memories,
        provider: str,
        current_message=None,
        chars_per_token: int = 4
    ):

        print(
            "========== TOKEN CONTEXT TRIMMING =========="
        )

        # ==========================================
        # PROVIDER VALIDATION
        # ==========================================

        if provider not in self.PROVIDER_LIMITS:

            print(
                f"ERROR: Unknown provider: {provider}"
            )

            raise NovaError(
                code=ErrorCode.PROVIDER_NOT_FOUND,
                message=f"Unknown provider: {provider}",
                source="token_budget_manager.py",
                status_code=404,
            )

        # ==========================================
        # GET CONVERSATION MESSAGES
        # ==========================================

        messages = conversation.get(
            "messages",
            []
        )

        # ==========================================
        # CREATE WORKING COPY
        # ==========================================

        trimmed_conversation = {
            "messages": sorted(
                messages,
                key=lambda x: x.get(
                    "createdAt",
                    ""
                )
            )
        }

        # ==========================================
        # PROVIDER BUDGET
        # ==========================================

        provider_budget = (
            self.PROVIDER_LIMITS[provider]["budget"]
        )

        print(
            f"PROVIDER: {provider}"
        )

        print(
            f"PROVIDER BUDGET: {provider_budget}"
        )

        print(
            f"ORIGINAL MESSAGE COUNT: "
            f"{len(trimmed_conversation['messages'])}"
        )

        # ==========================================
        # CALCULATE STATIC TOKEN COSTS
        #
        # Memories and current message do not change
        # while trimming conversation history.
        # ==========================================

        memories_tokens = self._estimate_tokens(
            memories,
            chars_per_token
        )

        message_tokens = self._estimate_tokens(
            current_message,
            chars_per_token
        )

        print(
            f"MEMORY TOKENS: {memories_tokens}"
        )

        print(
            f"CURRENT MESSAGE TOKENS: "
            f"{message_tokens}"
        )

        # ==========================================
        # CHECK IF STATIC CONTEXT ALREADY EXCEEDS
        # THE PROVIDER BUDGET
        # ==========================================

        static_tokens = (
            memories_tokens
            + message_tokens
        )

        if static_tokens > provider_budget:

            print(
                "WARNING: STATIC CONTEXT EXCEEDS "
                "PROVIDER BUDGET"
            )

            print(
                f"STATIC TOKENS: {static_tokens}"
            )

            print(
                f"PROVIDER BUDGET: {provider_budget}"
            )

            print(
                "Conversation history cannot fix "
                "this because memories/current message "
                "already exceed the budget."
            )

            print(
                "==========================================="
            )

            # Current message alone is too large.
            # This should be handled as an error by
            # the caller.
            if message_tokens > provider_budget:

                raise NovaError(
                    code=ErrorCode.MESSAGE_TOO_LARGE,
                    message=(
                        "Current message exceeds the "
                        "provider token budget."
                    ),
                    source="token_budget_manager.py",
                    status_code=413,
                )

            # Memories are consuming too much space.
            # Return no conversation history.
            return []

        # ==========================================
        # TRIMMING
        # ==========================================

        count = 0

        while True:

            # --------------------------------------
            # CALCULATE CONVERSATION TOKENS
            # --------------------------------------

            conversation_tokens = (
                self._estimate_tokens(
                    trimmed_conversation,
                    chars_per_token
                )
            )

            # --------------------------------------
            # CALCULATE TOTAL TOKENS
            # --------------------------------------

            total_tokens = (
                conversation_tokens
                + memories_tokens
                + message_tokens
            )

            print(
                f"TOTAL TOKENS: {total_tokens}/"
                f"{provider_budget}"
            )

            # ======================================
            # CONTEXT FITS THE BUDGET
            # ======================================

            if total_tokens <= provider_budget:

                print(
                    "CONTEXT FITS PROVIDER BUDGET"
                )

                break

            # ======================================
            # NO MORE CONVERSATION TO REMOVE
            # ======================================

            if not trimmed_conversation["messages"]:

                print(
                    "WARNING: ENTIRE CONVERSATION "
                    "WAS REMOVED"
                )

                print(
                    "The conversation history could "
                    "not fit within the provider budget."
                )

                break

            # ======================================
            # REMOVE OLDEST COMPLETE TURN
            # ======================================

            if (
                len(
                    trimmed_conversation["messages"]
                ) >= 2
            ):

                trimmed_conversation["messages"] = (
                    trimmed_conversation["messages"][2:]
                )

                count += 1

                print(
                    f"TRIMMED OLDEST TURN: {count}"
                )

                print(
                    f"REMAINING MESSAGES: "
                    f"{len(trimmed_conversation['messages'])}"
                )

            # ======================================
            # ONLY ONE MESSAGE REMAINS
            # ======================================

            else:

                trimmed_conversation["messages"] = []

                count += 1

                print(
                    "TRIMMED FINAL REMAINING MESSAGE"
                )

        # ==========================================
        # FINAL TOKEN CALCULATION
        # ==========================================

        final_conversation_tokens = (
            self._estimate_tokens(
                trimmed_conversation,
                chars_per_token
            )
        )

        final_total_tokens = (
            final_conversation_tokens
            + memories_tokens
            + message_tokens
        )

        # ==========================================
        # FINAL RESULT LOGS
        # ==========================================

        print(
            "========== TRIMMING COMPLETE =========="
        )

        print(
            f"TURNS REMOVED: {count}"
        )

        print(
            f"FINAL MESSAGE COUNT: "
            f"{len(trimmed_conversation['messages'])}"
        )

        print(
            f"FINAL CONVERSATION TOKENS: "
            f"{final_conversation_tokens}"
        )

        print(
            f"FINAL TOTAL TOKENS: "
            f"{final_total_tokens}/{provider_budget}"
        )

        print(
            "======================================="
        )

        return trimmed_conversation["messages"]

    # ==========================================
    # CHECK TOKENS
    # ==========================================

    def check_tokens(
        self,
        provider: str,
        context: ProviderContext,
        chars_per_token: int = 4
    ) -> bool:

        print(
            "========== TOKEN CHECK =========="
        )

        # ==========================================
        # PROVIDER VALIDATION
        # ==========================================

        if provider not in self.PROVIDER_LIMITS:

            print(
                f"ERROR: Unknown provider: {provider}"
            )

            raise NovaError(
                code=ErrorCode.PROVIDER_NOT_FOUND,
                message=f"Unknown provider: {provider}",
                source="token_budget_manager.py",
                status_code=404,
            )

        # ==========================================
        # TOKEN CALCULATION
        # ==========================================

        conversation_tokens = self._estimate_tokens(
            context.conversation,
            chars_per_token
        )

        memories_tokens = self._estimate_tokens(
            context.memories,
            chars_per_token
        )

        message_tokens = self._estimate_tokens(
            context.message,
            chars_per_token
        )

        # ==========================================
        # TOTAL TOKENS
        # ==========================================

        total_tokens = (
            conversation_tokens
            + memories_tokens
            + message_tokens
        )

        # ==========================================
        # PROVIDER BUDGET
        # ==========================================

        provider_budget = (
            self.PROVIDER_LIMITS[provider]["budget"]
        )

        # ==========================================
        # LOG RESULTS
        # ==========================================

        print(
            f"PROVIDER: {provider}"
        )

        print(
            f"CONVERSATION TOKENS: "
            f"{conversation_tokens}"
        )

        print(
            f"MEMORY TOKENS: "
            f"{memories_tokens}"
        )

        print(
            f"CURRENT MESSAGE TOKENS: "
            f"{message_tokens}"
        )

        print(
            f"TOTAL TOKENS: "
            f"{total_tokens}/{provider_budget}"
        )

        fits = (
            total_tokens <= provider_budget
        )

        print(
            f"CONTEXT FITS: {fits}"
        )

        print(
            "================================="
        )

        return fits

    # ==========================================
    # ESTIMATE TOKENS
    # ==========================================

    def _estimate_tokens(
        self,
        value,
        chars_per_token: int
    ) -> int:

        # ==========================================
        # NONE
        # ==========================================

        if value is None:
            return 0

        # ==========================================
        # STRING
        # ==========================================

        if isinstance(value, str):

            if not value:
                return 0

            return max(
                1,
                len(value) // chars_per_token
            )

        # ==========================================
        # DICTIONARY
        # ==========================================

        if isinstance(value, dict):

            total = 0

            for item in value.values():

                total += self._estimate_tokens(
                    item,
                    chars_per_token
                )

            return total

        # ==========================================
        # LIST / TUPLE
        # ==========================================

        if isinstance(value, (list, tuple)):

            total = 0

            for item in value:

                total += self._estimate_tokens(
                    item,
                    chars_per_token
                )

            return total

        # ==========================================
        # UNSUPPORTED TYPE
        # ==========================================

        return 0
