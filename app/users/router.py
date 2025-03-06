from fastapi import APIRouter

from app.core.config import settings
from app.dependencies.fastapi_users import fastapi_users

from .schemas import UserRead, UserUpdate

router = APIRouter(
    prefix=settings.api.v1.users,
    tags=["Users"],
)

router.include_router(
    router=fastapi_users.get_users_router(UserRead, UserUpdate),
)
