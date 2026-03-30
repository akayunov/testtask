import asyncio

from faststream import FastStream

from ps.messagebus.apps.payment import process_payments_on_start
from ps.messagebus.broker import broker

app = FastStream(broker)


async def main():
    await process_payments_on_start()
    # TODO check there are no messages created between process_payments_on_start and subscription
    await app.run()  # blocking method


def start():
    asyncio.run(main())
