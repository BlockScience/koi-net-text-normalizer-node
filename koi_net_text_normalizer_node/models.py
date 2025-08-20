from datetime import datetime
from pydantic import BaseModel


class NormalizedTextObject(BaseModel):
    text: str
    title: str | None = None
    author: str | None = None
    created_at: datetime | None = None
    edited_at: datetime | None = None