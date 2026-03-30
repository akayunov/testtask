import time
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ps.apps.auth import get_api_key
from ps.conf import QUEUE
from ps.messagebus.broker import router as fs_router
from ps.models import get_db
from ps.models.outbox import Outbox, Type
from ps.models.payment import Payment
from ps.schemas.payment import PaymentDetailed, PaymentIn, PaymentOut

router = APIRouter()


@router.post("/payments", status_code=status.HTTP_202_ACCEPTED)
async def create_payment(
    payment_data: PaymentIn,
    idempotency_key: Annotated[str, Header()],
    x_api_key: str = Depends(get_api_key),
    db: AsyncSession = Depends(get_db),
) -> PaymentOut:
    payment = (await db.scalars(select(Payment).where(Payment.idempotency_key == idempotency_key))).one_or_none()
    if payment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Payment with this idempotency_key already exists"
        )
    new_payment = Payment(
        total=payment_data.total,
        currency=payment_data.currency,
        description=payment_data.description,
        meta=payment_data.meta,
        webhook_url=payment_data.webhook_url,
        idempotency_key=idempotency_key,
        created_at=int(time.time()),
    )
    db.add(new_payment)
    await db.flush()
    outbox = Outbox(payment_id=new_payment.id, type=Type.PAYMENT)
    db.add(outbox)
    await db.commit()
    await fs_router.broker.publish(new_payment.to_dict(), queue=QUEUE)
    return new_payment


@router.get("/payments/{payment_id}")
async def get_payment(
    payment_id: int, x_api_key: str = Depends(get_api_key), db: AsyncSession = Depends(get_db)
) -> PaymentDetailed:
    payment = await db.get(Payment, payment_id)
    return payment
