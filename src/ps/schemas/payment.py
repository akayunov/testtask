from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ps.models.payment import Currency, PaymentStatus


class PaymentIn(BaseModel):
    total: Decimal
    currency: Currency
    description: str
    meta: dict[str, Any] = Field(default_factory=dict)
    webhook_url: str


class PaymentOut(BaseModel):
    id: int
    status: PaymentStatus
    created_at: int
    model_config = ConfigDict(from_attributes=True)


class PaymentDetailed(BaseModel):
    id: int
    total: Decimal
    currency: Currency
    description: str
    meta: dict[str, Any] = Field(default_factory=dict)
    status: PaymentStatus
    idempotency_key: str
    webhook_url: str
    created_at: int
    proceeded_at: int

    model_config = ConfigDict(from_attributes=True)
