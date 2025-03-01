from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.notes.services import delete_expired_notes


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(delete_expired_notes, 'interval', minutes=120)
    scheduler.start()
    return scheduler
