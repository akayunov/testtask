import enum
from decimal import Decimal

from sqlalchemy import Enum, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ps.models.base import Base


class Currency(enum.Enum):
    RUB = "rub"
    USD = "usd"
    EUR = "eur"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Payment(Base):
    __tablename__ = "payment"
    id: Mapped[int] = mapped_column(primary_key=True)
    total: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    currency: Mapped[Currency] = mapped_column(Enum(Currency))
    description: Mapped[str] = mapped_column(String(255))
    meta: Mapped[dict] = mapped_column(JSONB)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    idempotency_key: Mapped[str] = mapped_column(String(36), unique=True)
    webhook_url: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[int] = mapped_column(Integer, server_default="0")
    proceeded_at: Mapped[int] = mapped_column(Integer, server_default="0")

    outbox: Mapped["Outbox"] = relationship(back_populates="payment", cascade="all, delete-orphan")

    def to_dict(self):
        d = {field.name: getattr(self, field.name) for field in self.__table__.columns}
        d["total"] = str(d["total"])  # TODO use json encoder
        return d
