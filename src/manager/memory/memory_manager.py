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
# NOVA MEMORY MANAGER
# ==========================================

class NovaMemoryManager:

    def __init__(
        self,
        cache_manager: NovaCacheManager
    ):

        self.cache_manager = cache_manager

    # ==========================================
    # INVALIDATE USER MEMORY CACHE
    # ==========================================

    def invalidate_user_memory(
        self,
        user_uid: str
    ):

        cache_key = (
            f"memory:user:{user_uid}"
        )

        print(
            "========== MEMORY CACHE INVALIDATION =========="
        )

        print(
            f"CACHE KEY: {cache_key}"
        )

        self.cache_manager.delete(
            cache_key
        )

        print(
            "USER MEMORY CACHE INVALIDATED"
        )

        print(
            "==============================================="
        )

    # ==========================================
    # INVALIDATE CHAT MEMORY CACHE
    # ==========================================

    def invalidate_chat_memory(
        self,
        chat_uid: str
    ):

        cache_key = (
            f"memory:chat:{chat_uid}"
        )

        print(
            "========== MEMORY CACHE INVALIDATION =========="
        )

        print(
            f"CACHE KEY: {cache_key}"
        )

        self.cache_manager.delete(
            cache_key
        )

        print(
            "CHAT MEMORY CACHE INVALIDATED"
        )

        print(
            "==============================================="
        )

    # ==========================================
    # INVALIDATE MEMORY CACHES
    # ==========================================

    def invalidate_memory(
        self,
        user_uid: str,
        chat_uid: str | None = None
    ):

        # Every memory belongs to a user,
        # so always invalidate the user cache.

        self.invalidate_user_memory(
            user_uid
        )

        # If the memory belongs to a chat,
        # invalidate that chat cache too.

        if chat_uid is not None:

            self.invalidate_chat_memory(
                chat_uid
            )

    # ==========================================
    # GET CONTEXT
    # ==========================================

    def get_context(
        self,
        user_uid: str,
        chat_uid: str | None = None
    ):

        user_memories = self.get_memories(
            user_uid,
            True
        )

        chat_memories = None

        if chat_uid is not None:

            chat_memories = self.get_memories(
                user_uid,
                False,
                chat_uid
            )

        return {
            "user": user_memories,
            "chat": chat_memories
        }

    # ==========================================
    # GET MEMORIES
    # ==========================================

    def get_memories(
        self,
        user_uid: str,
        by_user: bool,
        chat_uid: str | None = None
    ):

        print(
            "========== MEMORY GET =========="
        )

        # ==========================================
        # CREATE CACHE KEY
        # ==========================================

        if by_user:

            cache_key = (
                f"memory:user:{user_uid}"
            )

        else:

            if chat_uid is None:

                raise ValueError(
                    "chat_uid is required when "
                    "by_user is False"
                )

            cache_key = (
                f"memory:chat:{chat_uid}"
            )

        print(
            f"CACHE KEY: {cache_key}"
        )

        # ==========================================
        # CHECK CACHE
        # ==========================================

        cache_memories = (
            self.cache_manager.get(
                cache_key
            )
        )

        if cache_memories is not None:

            print(
                "CACHE HIT"
            )

            print(
                "================================"
            )

            return cache_memories

        print(
            "CACHE MISS"
        )

        # ==========================================
        # GET USER MEMORIES
        # ==========================================

        if by_user:

            url = (
                f"{DATABASE_API_URL}"
                f"/users/{user_uid}/memories"
            )

            print(
                "MEMORY URL:",
                url
            )

        # ==========================================
        # GET CHAT MEMORIES
        # ==========================================

        else:

            url = (
                f"{DATABASE_API_URL}"
                f"/chats/{chat_uid}/memories"
            )

            print(
                "MEMORY URL:",
                url
            )

        # ==========================================
        # DATABASE REQUEST
        # ==========================================

        response = utils.apiPassage(
            "get",
            url
        )

        print(
            "Status:",
            response.status_code
        )

        memories = response.json()

        # ==========================================
        # SAVE TO CACHE
        # ==========================================

        self.cache_manager.set(
            cache_key,
            cache_value=memories,
            expiration=1800
        )

        print(
            "CACHED MEMORIES"
        )

        print(
            "================================"
        )

        return memories

    # ==========================================
    # CREATE MEMORY
    # ==========================================

    def create_memory(
        self,
        user_uid: str,
        memory_type: str,
        key: str,
        content: str,
        chat_uid: str | None = None
    ):

        url = (
            f"{DATABASE_API_URL}/memories"
        )

        response = utils.apiPassage(
            "post",
            url,
            {
                "chatUID": chat_uid,
                "content": content,
                "userUID": user_uid,
                "key": key,
                "type": memory_type
            }
        )

        print(
            "========== MEMORY CREATE =========="
        )

        print(
            "URL:",
            url
        )

        print(
            "Status:",
            response.status_code
        )

        print(
            "Response:",
            response.text
        )

        # ==========================================
        # INVALIDATE CACHE
        # ==========================================

        if response.ok:

            self.invalidate_memory(
                user_uid=user_uid,
                chat_uid=chat_uid
            )

        print(
            "==================================="
        )

        return response

    # ==========================================
    # UPDATE MEMORY
    # ==========================================

    def update_memory(
        self,
        memory_uid: str,
        content: str,
        key: str,
        memory_type: str,
        user_uid: str | None = None,
        chat_uid: str | None = None
    ):

        url = (
            f"{DATABASE_API_URL}"
            f"/memories/{memory_uid}"
        )

        response = utils.apiPassage(
            "patch",
            url,
            {
                "content": content,
                "key": key,
                "type": memory_type
            }
        )

        print(
            "========== MEMORY UPDATE =========="
        )

        print(
            "URL:",
            url
        )

        print(
            "Status:",
            response.status_code
        )

        print(
            "Response:",
            response.text
        )

        # ==========================================
        # INVALIDATE CACHE
        # ==========================================

        if response.ok and user_uid is not None:

            self.invalidate_memory(
                user_uid=user_uid,
                chat_uid=chat_uid
            )

        print(
            "==================================="
        )

        return response

    # ==========================================
    # DELETE MEMORY
    # ==========================================

    def delete_memory(
        self,
        memory_uid: str,
        user_uid: str | None = None,
        chat_uid: str | None = None
    ):

        url = (
            f"{DATABASE_API_URL}"
            f"/memories/{memory_uid}"
        )

        response = utils.apiPassage(
            "delete",
            url
        )

        print(
            "========== MEMORY DELETE =========="
        )

        print(
            "URL:",
            url
        )

        print(
            "Status:",
            response.status_code
        )

        print(
            "Response:",
            response.text
        )

        # ==========================================
        # INVALIDATE CACHE
        # ==========================================

        if response.ok and user_uid is not None:

            self.invalidate_memory(
                user_uid=user_uid,
                chat_uid=chat_uid
            )

        print(
            "==================================="
        )

        return response
