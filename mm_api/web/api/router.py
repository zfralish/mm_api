from fastapi.routing import APIRouter

from mm_api.web.api import bird, dummy, echo, falconer, monitoring, redis

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
api_router.include_router(falconer.router, tags=["falconer"])
api_router.include_router(bird.router, tags=["bird"])
