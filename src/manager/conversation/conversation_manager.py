from ...utils.Utils import NovaUtils
from ..cache.cache_manager import NovaCacheManager
import os

from dotenv import load_dotenv

load_dotenv()


# ==========================================
# ENVIRONMENT
# ==========================================

ENVIRONMENT = os.getenv(
    "ENVIRONMENT",
    "development"
).lower()


# ==========================================
# DATABASE API URL
# ==========================================

if ENVIRONMENT == "production":

    DATABASE_API_URL = os.getenv(
        "GLOBAL_DATABASE_API_URL"
    )

elif ENVIRONMENT == "development":

    DATABASE_API_URL = os.getenv(
        "LOCAL_DATABASE_API_URL"
    )

else:

    raise RuntimeError(
        f"Invalid ENVIRONMENT: {ENVIRONMENT}. "
        "Use 'development' or 'production'."
    )


if DATABASE_API_URL is None:

    raise RuntimeError(
        f"Database API URL is not configured for "
        f"environment: {ENVIRONMENT}"
    )


utils = NovaUtils()


# ==========================================
# NOVA CONVERSATION MANAGER
# ==========================================

class NovaConversationManager:

    def __init__(
        self,
        cache_manager: NovaCacheManager
    ):

        self.cache_manager = cache_manager
        self.message_cap: int = 10 * 2

    # ==========================================
    # INVALIDATE CONVERSATION CACHE
    # ==========================================

    def invalidate_conversation(
        self,
        chat_uid: str
    ):

        cache_key = (
            f"conversation:{chat_uid}"
        )

        print(
            "========== CONVERSATION INVALIDATION =========="
        )

        print(
            f"CACHE KEY: {cache_key}"
        )

        self.cache_manager.delete(
            cache_key
        )

        print(
            "CONVERSATION CACHE INVALIDATED"
        )

        print(
            "==============================================="
        )

    # ==========================================
    # GET CONTEXT
    # ==========================================

    def get_context(
        self,
        chat_uid: str
    ):

        # ==========================================
        # INVALIDATE BEFORE PROCESSING
        # ==========================================

        self.invalidate_conversation(
            chat_uid
        )

        # ==========================================
        # GET CONVERSATIONS
        # ==========================================

        chat_messages = self.get_conversations(
            chat_uid
        )

        # ==========================================
        # MESSAGE CAP
        # ==========================================

        messages = chat_messages[
            -self.message_cap:
        ]

        print(
            "messages:",
            messages
        )

        print(
            f"Conversation context: "
            f"{len(messages)}/{self.message_cap} messages "
            f"({len(messages) // 2}/"
            f"{self.message_cap // 2} turns)"
        )

        print(
            "================================"
        )

        return {
            "messages": messages,
        }

    # ==========================================
    # GET CONVERSATIONS
    # ==========================================

    def get_conversations(
        self,
        chat_uid: str,
    ):

        print(
            "========== CONVERSATION GET =========="
        )

        # ==========================================
        # CREATE CACHE KEY
        # ==========================================

        cache_key = (
            f"conversation:{chat_uid}"
        )

        print(
            f"CACHE KEY: {cache_key}"
        )

        # ==========================================
        # CHECK CACHE
        # ==========================================

        cache_messages = (
            self.cache_manager.get(
                cache_key
            )
        )

        if cache_messages is not None:

            print(
                "CACHE HIT"
            )

            print(
                "================================"
            )

            return cache_messages

        print(
            "CACHE MISS"
        )

        # ==========================================
        # DATABASE REQUEST
        # ==========================================

        url = (
            f"{DATABASE_API_URL}"
            f"/chats/{chat_uid}/messages"
        )

        print(
            "CONVERSATION URL:",
            url
        )

        response = utils.apiPassage(
            "get",
            url
        )

        messages = (
            response.json()["message Info"]
        )

        print(
            "Status:",
            response.status_code
        )

        # ==========================================
        # SAVE TO CACHE
        # ==========================================

        self.cache_manager.set(
            cache_key,
            cache_value=messages,
            expiration=600
        )

        print(
            "CACHED CONVERSATION"
        )

        print(
            "================================"
        )

        return messages
