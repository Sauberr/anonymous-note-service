import uvicorn
from fastapi.staticfiles import StaticFiles
from sqladmin import Admin

from app.admin.views import NoteAdmin, UserAdmin, AccessTokensAdmin, OAuthAccountAdmin
from app.core.config import settings
from app.create_fastapi_app import create_app
from app.core.models.db_helper import db_helper
from app.api.router import router as api_router

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


main_app.include_router(
    api_router,
)


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
