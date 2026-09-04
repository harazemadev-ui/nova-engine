from pydantic import BaseModel


class NovaRequest(BaseModel):
    message: str
    provider: str
    version: str
    userUID: str
    chatUID: str
