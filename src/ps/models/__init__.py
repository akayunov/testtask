from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ps.conf import POSTGRESS_URL
from ps.models.outbox import Outbox
from ps.models.payment import Payment

__all__ = ["Payment", "Outbox"]

engine = create_async_engine(POSTGRESS_URL)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
