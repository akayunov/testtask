import asyncio
import functools
import logging
import random
import time

import aiohttp
from faststream.rabbit import RabbitQueue
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ps.conf import DLQ, PAYMENT_GATEWAY_RETRY_COUNT, QUEUE, WEBHOOK_RETRY_COUNT
from ps.messagebus.broker import broker
from ps.models import AsyncSessionLocal, Outbox, Payment
from ps.models.outbox import OutboxStatus
from ps.models.payment import PaymentStatus
from ps.schemas.payment import PaymentDetailed

queue = RabbitQueue(QUEUE, durable=True)
session = None
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def retry(retry_count=WEBHOOK_RETRY_COUNT, delay=1):
    def dec(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            i = 0
            for i in range(retry_count):
                try:
                    return await fn(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Webhook notify exception: {e}, try {i + 1}")
                if i < retry_count - 1:
                    await asyncio.sleep(delay * 2 ** (i + 1))
            logger.info(f"All tries are used, try {i + 1}")

        return wrapper

    return dec


@retry(retry_count=WEBHOOK_RETRY_COUNT, delay=1)
async def notify_webhook(payment):
    global session
    if not session:
        session = aiohttp.ClientSession()
    async with session.get(payment.webhook_url) as response:
        if response.status != 200:
            raise Exception(f"Http error on: {payment.webhook_url} - {response.status}")


async def payment_gateway_logic(payment):
    await asyncio.sleep(random.randint(2, 5))
    if random.randint(0, 9) == 9:
        raise Exception('Some exception happened in payment gateway')


async def process_payment(payment_msg):
    async with AsyncSessionLocal() as db:
        logger.info(f'process payment: {payment_msg}')
        try:
            payment = await db.get(Payment, payment_msg.id)
            outbox_entity = (await db.scalars(select(Outbox).where(Outbox.payment_id == payment_msg.id))).one()
            if payment.status == PaymentStatus.SUCCEEDED:
                outbox_entity.status = OutboxStatus.SUCCEEDED
                return
            await payment_gateway_logic(payment)
            payment.status = PaymentStatus.SUCCEEDED
            payment.proceeded_at = int(time.monotonic())
        except Exception as e:
            logger.error(f'process payment Exception: {e}')
            if outbox_entity.attempts >= PAYMENT_GATEWAY_RETRY_COUNT:
                d = payment_msg.dict()
                d["total"] = str(d["total"])  # TODO json encoder
                d["currency"] = d["currency"].value  # TODO json encoder
                d["status"] = d["status"].value  # TODO json encoder
                await broker.publish(d, queue=DLQ)
                payment.status = PaymentStatus.FAILED
                outbox_entity.status = OutboxStatus.FAILED
                return
            outbox_entity.status = OutboxStatus.RETRYING
            outbox_entity.attempts = outbox_entity.attempts + 1
            delay = 2**outbox_entity.attempts
            outbox_entity.scheduled_at = int(time.monotonic()) + delay
            logger.info(f"Delay failed payment {payment} for {int(time.monotonic()) + delay}")
            asyncio.create_task(process_payment_delayed(delay, payment_msg))
        finally:
            logger.info("Do commit")
            await db.commit()
    await notify_webhook(payment)


async def process_payments_on_start():
    async with AsyncSessionLocal() as db:
        stmt = select(Outbox).options(joinedload(Outbox.payment)).where(Outbox.status == OutboxStatus.RETRYING)
        result = await db.scalars(stmt)
        for outbox_item in result.all():
            payment_msg = PaymentDetailed.model_validate(outbox_item.payment)
            await process_payment(payment_msg)


async def process_payment_delayed(delay, payment_msg):
    logger.info(f'process delayed payment: {payment_msg}')
    await asyncio.sleep(delay)
    await process_payment(payment_msg)


@broker.subscriber(queue)
async def handle_msg(payment_msg: PaymentDetailed):
    await process_payment(payment_msg)
