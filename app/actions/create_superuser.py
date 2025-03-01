import asyncio

import contextlib

from app.dependencies.user_manager import get_user_manager
from app.dependencies.users import get_users_db

from app.utils import get_async_session
from app.authentication.user_manager import UserManager
from app.users.schemas import UserCreate
from app.users.models import User

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_users_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(
        user_manager: UserManager,
        user_create: UserCreate,
) -> User:
    user = await user_manager.create(
        user_create=user_create,
        safe=False,
    )
    return user


async def create_superuser(user):
    pass


if __name__ == "__main__":
    asyncio.run(create_superuser())
    