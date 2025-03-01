from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NoteBase(BaseModel):
    text: str
    secret: str
    note_hash: str = None
    is_ephemeral: Optional[bool] = False
    lifetime: Optional[datetime] = None
    image: Optional[str] = None


class NoteID(BaseModel):
    note_id: str
    note_secret: str
