from typing import TYPE_CHECKING

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.orm import Mapped, relationship

from app.authentication.model import OAuthAccount
from app.core.baseclass import Base
from app.core.types.user_id import UserIdType
from app.mixin.mixin import IdIntMixin

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class User(Base, IdIntMixin, SQLAlchemyBaseUserTable[UserIdType]):
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(
        "OAuthAccount", lazy="joined"
    )

    @classmethod
    def get_db(cls, session: "AsyncSession"):
        return SQLAlchemyUserDatabase(session, cls)
