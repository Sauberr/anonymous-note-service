import uvicorn
from fastapi import Depends
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin

from app.admin.views import NoteAdmin, UserAdmin, AccessTokensAdmin, OAuthAccountAdmin
from app.authentication.messages import router as message_router
from app.authentication.router import router as auth_router
from app.core.config import settings
from app.notes.router import router as note_router
from app.users.router import router as user_router
from app.webhooks.user import router as webhook_router
from app.create_fastapi_app import create_app
from app.core.models.db_helper import db_helper

main_app = create_app()
main_app.mount("/static", StaticFiles(directory="app/static"), name="static")

admin = Admin(
    main_app,
    db_helper.engine,
    title="FastAPI Admin",
    base_url="/admin",
    logo_url="static/images/logo.png",
)

admin.add_view(UserAdmin)
admin.add_view(NoteAdmin)
admin.add_view(AccessTokensAdmin)
admin.add_view(OAuthAccountAdmin)

http_bearer = HTTPBearer(auto_error=True)

main_app.include_router(
    note_router,
)
main_app.include_router(
    user_router,
    dependencies=[Depends(http_bearer)],
)
main_app.include_router(auth_router)
main_app.include_router(message_router)

main_app.include_router(webhook_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
