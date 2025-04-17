from fastapi import status
from fastapi.responses import JSONResponse

from .router import auth_router


@auth_router.post("/token")
async def update_access_token():
    # TODO implement token refresh
    return JSONResponse({}, status.HTTP_403_FORBIDDEN)
