from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from app.authentication.oauth2 import google_oauth_client
from app.core.config import settings
from app.dependencies.backend import authentication_backend
from app.dependencies.fastapi_users import fastapi_users
from app.users.schemas import UserCreate, UserRead

router = APIRouter(
    prefix=settings.api.v1.auth,
    tags=["Auth"],
)

templates = Jinja2Templates(directory="app/templates")


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
    fastapi_users.get_oauth_router(
        google_oauth_client, authentication_backend, "SECRET", associate_by_email=True
    ),
    prefix="/google",
)

router.include_router(
    fastapi_users.get_oauth_associate_router(google_oauth_client, UserRead, "SECRET"),
    prefix="/associate/google",
)


router.include_router(
    fastapi_users.get_verify_router(UserRead),
)

router.include_router(
    fastapi_users.get_reset_password_router(),
)
