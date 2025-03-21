from fastapi import APIRouter

from app.core.config import settings
from app.api.api_v1.router import router as router_api_v1

router = APIRouter(
    prefix=settings.api.prefix,
)
router.include_router(router_api_v1)
