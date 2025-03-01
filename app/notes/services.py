from datetime import datetime, timezone
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.notes.models import NoteORM
from app.db_session import async_session_maker
import hashlib


def get_note_id(text: str, salt: str) -> str:
    return hashlib.sha256(
        text.encode("UTF-8") + salt.encode("UTF-8")
    ).hexdigest()


async def is_lifetime_note(note: NoteORM, db: AsyncSession):
    if note.lifetime and datetime.now(timezone.utc) > note.lifetime:
        await db.delete(note)
        await db.commit()
        return True
    return False


async def is_ephemeral_note(note: NoteORM, db: AsyncSession):
    if note.is_ephemeral:
        await db.delete(note)
        await db.commit()
        return True
    return False


async def delete_expired_notes():
    async with async_session_maker() as session:
        async with session.begin():
            current_time = datetime.now(timezone.utc)
            result = await session.execute(select(NoteORM).where(NoteORM.lifetime <= current_time))
            expired_notes = result.scalars().all()
            for note in expired_notes:
                await session.delete(note)
            await session.commit()
