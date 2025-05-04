from fastapi import FastAPI
from sqladmin import Admin

from app.admin.views import (AccessTokensAdmin, NoteAdmin, OAuthAccountAdmin,
                             UserAdmin)
from app.core.models.db_helper import db_helper


def setup_admin(app: FastAPI):
    admin = Admin(
        app,
        db_helper.engine,
        title="FastAPI Admin",
        base_url="/admin",
        logo_url="static/images/logo.png",
    )

    admin.add_view(UserAdmin)
    admin.add_view(NoteAdmin)
    admin.add_view(AccessTokensAdmin)
    admin.add_view(OAuthAccountAdmin)

    return admin
