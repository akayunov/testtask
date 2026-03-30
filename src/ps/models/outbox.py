import enum

from sqlalchemy import Enum, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ps.models.base import Base


class Type(enum.Enum):
    PAYMENT = "payment"


class OutboxStatus(enum.Enum):
    PENDING = "pending"
    RETRYING = "retrying"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class Outbox(Base):
    __tablename__ = "outbox"
    id: Mapped[int] = mapped_column(primary_key=True)
    payment_id: Mapped[int] = mapped_column(ForeignKey("payment.id"))
    type: Mapped[Type]
    status: Mapped[OutboxStatus] = mapped_column(Enum(OutboxStatus), default=OutboxStatus.PENDING)
    attempts: Mapped[int] = mapped_column(server_default=text("0"))
    last_attempt: Mapped[int] = mapped_column(Integer, server_default="0")
    created_at: Mapped[int] = mapped_column(Integer, server_default="0")
    scheduled_at: Mapped[int] = mapped_column(Integer, server_default="0")
    error: Mapped[str] = mapped_column(String(255), default="")

    payment: Mapped["Payment"] = relationship(back_populates="outbox")
