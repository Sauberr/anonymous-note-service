import os

from app.core.config import settings

os.environ.setdefault("ADMIN_USER_MODEL", "User")
os.environ.setdefault("ADMIN_USER_MODEL_USERNAME_FIELD", "email")
os.environ.setdefault("ADMIN_SECRET_KEY", settings.access_token.reset_password_token_secret)
os.environ.setdefault("ADMIN_SITE_NAME", "🔒 Notes Admin")
os.environ.setdefault("ADMIN_PRIMARY_COLOR", "#6366f1")
os.environ.setdefault("ADMIN_DATE_FORMAT", "DD.MM.YYYY")
os.environ.setdefault("ADMIN_DATETIME_FORMAT", "DD.MM.YYYY HH:mm")
os.environ.setdefault("ADMIN_PREFIX", "admin")

from fastapi import FastAPI  # noqa: E402
from fastadmin import fastapi_app as admin_app  # noqa: E402

import app.admin.views  # noqa: E402, F401


def setup_admin(fastapi_app: FastAPI) -> None:
    fastapi_app.mount("/admin", admin_app)
