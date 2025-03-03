from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.users.models import User
from app.utils.async_session import get_async_session

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_users_db(
    session: Annotated[
        "AsyncSession",
        Depends(get_async_session),
    ],
):
    yield User.get_db(session=session)
