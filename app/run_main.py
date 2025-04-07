from app.core.gunicorn.application import Application
from app.core.gunicorn.app_options import get_app_options
from app.main import main_app
from app.core.config import settings


def main():
    Application(
        application=main_app,
        options=get_app_options(
            host=settings.gunicorn.host,
            port=settings.gunicorn.port,
            timeout=settings.gunicorn.timeout,
            workers=settings.gunicorn.workers,
            log_level=settings.logging.log_level,
        ),
    ).run()


if __name__ == "__main__":
    main()
