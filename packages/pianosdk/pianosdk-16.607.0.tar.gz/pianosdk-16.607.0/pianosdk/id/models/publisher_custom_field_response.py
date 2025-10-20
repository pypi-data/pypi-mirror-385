from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PublisherCustomFieldResponse(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None


PublisherCustomFieldResponse.model_rebuild()
