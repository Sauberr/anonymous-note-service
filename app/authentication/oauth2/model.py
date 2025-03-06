from fastapi_users_db_sqlalchemy import SQLAlchemyBaseOAuthAccountTable
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.core.baseclass import Base
from app.core.types.user_id import UserIdType
from app.mixin.mixin import IdIntMixin


class OAuthAccount(Base, IdIntMixin, SQLAlchemyBaseOAuthAccountTable[UserIdType]):
    user_id: Mapped[UserIdType] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="cascade"),
        nullable=False,
    )

    @declared_attr
    def user_id(cls) -> Mapped[UserIdType]:
        return mapped_column(
            Integer, ForeignKey("users.id", ondelete="cascade"), nullable=False
        )
