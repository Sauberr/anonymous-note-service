from pydantic import BaseModel


class MessageErrorSchema(BaseModel):
    response: str
    message: str