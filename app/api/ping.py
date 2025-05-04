from .router import api_router


@api_router.get("/ping")
async def ping() -> str:
    return "pong"
