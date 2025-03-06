import asyncio
import contextlib

from pydantic import EmailStr

from app.authentication.user_manager import UserManager
from app.core.config import settings
from app.dependencies.user_manager import get_user_manager
from app.dependencies.users import get_users_db
from app.users.models import User
from app.users.schemas import UserCreate
from app.utils.async_session import get_async_session

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_users_db_context = contextlib.asynccontextmanager(get_users_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


default_email: str = settings.DEFAULT_EMAIL
default_password: str = settings.DEFAULT_PASSWORD
default_is_active: bool = True
default_is_superuser: bool = True
default_is_verified: bool = True


async def create_user(
    user_manager: UserManager,
    user_create: UserCreate,
) -> User:
    user = await user_manager.create(
        user_create=user_create,
        safe=False,
    )
    return user


async def create_superuser(
    email: EmailStr = default_email,
    password: str = default_password,
    is_active: bool = default_is_active,
    is_superuser: bool = default_is_superuser,
    is_verified: bool = default_is_verified,
):
    user_create = UserCreate(
        email=email,
        password=password,
        is_active=is_active,
        is_superuser=is_superuser,
        is_verified=is_verified,
    )

    async with get_async_session_context() as session:
        async with get_users_db_context(session) as users_db:
            async with get_user_manager_context(users_db) as user_manager:
                return await create_user(
                    user_manager=user_manager,
                    user_create=user_create,
                )


if __name__ == "__main__":
    asyncio.run(create_superuser())
