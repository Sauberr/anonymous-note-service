from fastapi import FastAPI
from fastapi_babel import BabelMiddleware

from app.localization import babel_configs


def setup_middleware(app: FastAPI) -> None:
    """
    Setup middleware for the FastAPI application.
    """
    app.add_middleware(
        BabelMiddleware,
        babel_configs=babel_configs,
        locale_selector=lambda request: request.cookies.get("locale", "en"),
    )
