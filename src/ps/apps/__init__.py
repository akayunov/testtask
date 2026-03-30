from contextlib import asynccontextmanager

from fastapi import FastAPI

from ps.apps.payment import router as router_v1
from ps.messagebus.broker import router as fs_router


@asynccontextmanager
async def my_lifespan(app: FastAPI):
    async with fs_router.broker:
        yield


app = FastAPI(title="Payment API", lifespan=my_lifespan)

app.include_router(router_v1, prefix="/api/v1", tags=["v1"])
