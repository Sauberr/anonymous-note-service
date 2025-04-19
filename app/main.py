import logging

import uvicorn
from fastapi.staticfiles import StaticFiles

from app.admin.admin_panel import setup_admin
from app.api.router import router as api_router
from app.core.config import settings
from app.create_fastapi_app import create_app
from app.localization import babel
from app.middleware import setup_middleware

logging.basicConfig(
    level=settings.logging.log_level,
    format=settings.logging.log_format,
)

main_app = create_app(
    create_custom_static_urls=True,
)

main_app.mount("/static", StaticFiles(directory="app/static"), name="static")

setup_middleware(
    main_app,
)

admin = setup_admin(
    main_app,
)

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
    babel.run_cli()
