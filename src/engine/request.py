from pydantic import BaseModel

from ..moduledata.context import ModuleContext


class NovaRequest(BaseModel):
    message: str
    module: str
    version: str
    userUID: str
    chatUID: str | None = None

    def create_module_context(self, memories):
        return ModuleContext(
            message=self.message,
            userUID=self.userUID,
            chatUID=self.chatUID,
            memories=memories
        )
