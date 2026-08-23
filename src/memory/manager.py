from ..utils.Utils import NovaUtils
import os

from dotenv import load_dotenv

load_dotenv()

ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
DATABASE_API_URL = os.getenv("DATABASE_API_URL")

if DATABASE_API_URL is None:
    raise RuntimeError("DATABASE_API_URL is not configured")

utils = NovaUtils()


class NovaMemoryManager:

    def __init__(self):
        pass

    def get_context(self, user_uid: str, chat_uid: str | None = None):
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

    def get_memories(self, user_uid: str, by_user: bool, chat_uid: str | None = None):
        print("========== MEMORY GET ==========")
        print("URL:", f"{DATABASE_API_URL}/users/{user_uid}/memories")
        if by_user:
            response = utils.apiPassage(
                "get",
                f"{DATABASE_API_URL}/users/{user_uid}/memories"
            )

            return response.json()

        if chat_uid is None:
            raise ValueError(
                "chat_uid is required when by_user is False"
            )

        response = utils.apiPassage(
            "get",
            f"{DATABASE_API_URL}/chats/{chat_uid}/memories"
        )

        print("Status:", response.status_code)
        print("Content-Type:", response.headers.get("content-type"))
        print("Response:", repr(response.text))
        print("================================")

        return response.json()

    def create_memory(self, user_uid: str, memory_type: str, key: str, content: str, chat_uid: str | None = None):
        response = utils.apiPassage(
            "post",
            f"{DATABASE_API_URL}/memories",
            {
                "chatUID": chat_uid,
                "content": content,
                "userUID": user_uid,
                "key": key,
                "type": memory_type
            }
        )

        print("========== MEMORY CREATE ==========")
        print("Status:", response.status_code)
        print("Response:", response.text)
        print("===================================")

        return response

    def update_memory(self, memory_uid: str, content: str, key: str, memory_type: str):
        return utils.apiPassage("patch", f"{DATABASE_API_URL}/memories/{memory_uid}", {
            "content": content,
            "key": key,
            "type": memory_type
        })

    def delete_memory(self, memory_uid: str):
        return utils.apiPassage(
            "delete", f"{DATABASE_API_URL}/memories/{memory_uid}",)
