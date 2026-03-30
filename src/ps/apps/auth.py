from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette import status

from ps.conf import API_KEY_NAME, VALID_API_KEY

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == VALID_API_KEY:
        return api_key
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate API Key")
