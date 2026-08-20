from ..moduledata.context import ModuleContext
from pydantic import BaseModel


class NovaRequest(BaseModel):
    message: str
    module: str
    version: str

    def create_module_context(self) -> ModuleContext:
        module_context = ModuleContext(self.message)
        return module_context
