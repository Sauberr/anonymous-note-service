from typing import Optional
from sqlalchemy.future import select
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from dependencies.fastapi_users import get_user_manager
from app.core.models.db_helper import db_helper
from app.users.models import User


class AdminAuth:
    ...