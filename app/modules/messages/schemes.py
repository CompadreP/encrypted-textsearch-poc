import datetime

from pydantic import BaseModel


class MessageScheme(BaseModel):
    text: str
    created_at: datetime.datetime


class OpenSearchResultScheme(BaseModel):
    id: int
    encrypted_text: str
