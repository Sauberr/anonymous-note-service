from pydantic import BaseModel


class MessageErrorSchema(BaseModel):
    error: str