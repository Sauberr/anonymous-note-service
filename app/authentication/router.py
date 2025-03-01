from fastapi import APIRouter
from app.dependencies.fastapi_users import fastapi_users
from app.dependencies.backend import authentication_backend
from app.users.schemas import UserCreate, UserRead

auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


auth_router.include_router(
    router=fastapi_users.get_auth_router(
        authentication_backend,
    ),
)


auth_router.include_router(
    router=fastapi_users.get_register_router(
        UserRead,
        UserCreate,
    ),
)
