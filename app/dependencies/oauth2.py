from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.authentication.models import OAuthAccount
from app.users.models import User
from app.core.models.db_helper import db_helper

if TYPE_CHECKING:
    from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_user_db(
    session: Annotated[
        "AsyncSession",
        Depends(db_helper.session_getter),
    ],
):
    yield SQLAlchemyUserDatabase(session, User, OAuthAccount)
