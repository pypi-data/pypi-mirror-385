from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class BillingTimingOption(BaseModel):
    value: Optional[str] = None
    name: Optional[str] = None
    prorate_disabled: Optional[bool] = None
    secure_enabled: Optional[bool] = None


BillingTimingOption.model_rebuild()
