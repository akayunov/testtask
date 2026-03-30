from fastapi import APIRouter, FastAPI, HTTPException, status

router = APIRouter()

REQUEST_REGISTRY = {}


@router.get("/webhook/{request_id}/{retry_count}", status_code=status.HTTP_200_OK)
async def webhook(request_id: str, retry_count: int):
    if request_id not in REQUEST_REGISTRY:
        REQUEST_REGISTRY[request_id] = retry_count - 1
    else:
        REQUEST_REGISTRY[request_id] -= 1
    if REQUEST_REGISTRY[request_id] >= 0:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Try to retry")


app = FastAPI(title="Webhook processor mock")
app.include_router(router, prefix="/api/v1", tags=["v1"])
