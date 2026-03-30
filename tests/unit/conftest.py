import asyncio

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from ps import conf
from ps.models.base import Base


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(conf.POSTGRESS_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(engine):
    async with engine.connect() as conn:
        session = AsyncSession(bind=conn, expire_on_commit=False)
        yield session
