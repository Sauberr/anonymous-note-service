from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.authentication.oauth2.model import OAuthAccount
from app.users.models import User
from app.utils.async_session import get_async_session

if TYPE_CHECKING:
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_db(
    session: Annotated[
        "AsyncSession",
        Depends(get_async_session),
    ],
):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)
