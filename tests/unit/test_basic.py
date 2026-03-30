import random
import time
import uuid

import pytest
from sqlalchemy import select

from ps.messagebus.apps.payment import process_payments_on_start
from ps.models import Outbox, Payment
from ps.models.outbox import OutboxStatus, Type
from ps.models.payment import Currency, PaymentStatus


@pytest.mark.asyncio(loop_scope="session")
async def test_process_delayed_payment_on_start(db_session):
    for i in range(10):
        p = Payment(
            total=i,
            currency=Currency.RUB,
            description=f"some desc for {i} payment",
            meta={},
            webhook_url=f'http://payment-webhook-mock:9999/api/v1/webhook/{random.randint(1, 1000)}/0',
            idempotency_key=uuid.uuid4().hex,
            created_at=int(time.time()),
        )
        db_session.add(p)
        await db_session.flush()
        o = Outbox(payment_id=p.id, type=Type.PAYMENT, status=OutboxStatus.RETRYING)
        db_session.add(o)

    await db_session.commit()

    await process_payments_on_start()

    await db_session.commit()
    db_session.expire_all()
    stmt = select(Payment)
    result = await db_session.scalars(stmt)
    for pp in result.all():
        assert pp.status == PaymentStatus.SUCCEEDED
