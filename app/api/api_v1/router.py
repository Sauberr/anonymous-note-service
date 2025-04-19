from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.authentication.messages import router as message_router
from app.authentication.router import router as auth_router
from app.core.config import settings
from app.notes.router import router as note_router
from app.users.router import router as user_router
from app.webhooks.user import router as webhook_router

http_bearer = HTTPBearer(auto_error=True)

router = APIRouter(
    prefix=settings.api.v1.prefix,
)

router.include_router(
    note_router,
)
router.include_router(
    user_router,
    dependencies=[Depends(http_bearer)],
)
router.include_router(auth_router)
router.include_router(message_router)

router.include_router(webhook_router)
