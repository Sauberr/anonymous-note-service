from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column, Mapped

from app.baseclass import Base
from app.mixin.mixin import IdIntMixin


class NoteORM(Base, IdIntMixin):
    __tablename__ = "notes"

    text: Mapped[str] = mapped_column(nullable=False)
    secret: Mapped[str] = mapped_column(nullable=False)
    note_hash: Mapped[str] = mapped_column(default=None)
    is_ephemeral: Mapped[bool] = mapped_column(default=False, nullable=False)
    lifetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    image: Mapped[str] = mapped_column(nullable=True)
