from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.models.db_helper import db_helper
from app.core.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    scheduler = start_scheduler()

    yield
    scheduler.shutdown()
    await db_helper.dispose()
