from fastapi import APIRouter

from app.dependencies.backend import authentication_backend
from app.dependencies.fastapi_users import fastapi_users
from app.users.schemas import UserCreate, UserRead

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


router.include_router(
    router=fastapi_users.get_auth_router(
        authentication_backend,
        requires_verification=False,
    ),
)

router.include_router(
    router=fastapi_users.get_register_router(
        UserRead,
        UserCreate,
    ),
)

router.include_router(
    fastapi_users.get_verify_router(UserRead),
)

router.include_router(
    fastapi_users.get_reset_password_router(),
)
