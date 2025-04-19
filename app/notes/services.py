import hashlib
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.models.db_helper import DataBaseHelper
from app.notes.models import Note


def get_note_id(text: str, salt: str) -> str:
    return hashlib.sha256(text.encode("UTF-8") + salt.encode("UTF-8")).hexdigest()


async def is_lifetime_note(note: Note, db: AsyncSession):
    if note.lifetime and datetime.now(timezone.utc) > note.lifetime:
        await db.delete(note)
        await db.commit()
        return True
    return False


async def is_ephemeral_note(note: Note, db: AsyncSession):
    if note.is_ephemeral:
        await db.delete(note)
        await db.commit()
        return True
    return False


async def delete_expired_notes(db_helper: DataBaseHelper):
    async for session in db_helper.session_getter():
        try:
            current_time = datetime.now(timezone.utc)
            result = await session.execute(
                select(Note).where(Note.lifetime <= current_time)
            )
            expired_notes = result.scalars().all()

            for note in expired_notes:
                await session.delete(note)

            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
