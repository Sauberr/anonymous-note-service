from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.notes.services import delete_expired_notes
from app.core.models.db_helper import db_helper


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(delete_expired_notes, "interval", minutes=120, args=[db_helper])
    scheduler.start()
    return scheduler
