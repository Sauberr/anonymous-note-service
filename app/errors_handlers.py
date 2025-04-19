import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from fastapi_babel import _
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError

log = logging.getLogger(__name__)


def register_errors_handlers(app: FastAPI) -> None:

    @app.exception_handler(ValidationError)
    def handle_pydantic_validation_error(
        request: Request, exc: ValidationError
    ) -> ORJSONResponse:
        return ORJSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": _("Unhandled error"), "error": exc.errors()},
        )

    @app.exception_handler(DatabaseError)
    def handle_db_error(request: Request, exc: DatabaseError) -> ORJSONResponse:
        log.error(
            _("Unhandled database error"),
            exc_info=exc,
        )
        return ORJSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message": _("An unexpected error has occurred"),
            },
        )


def error_response(
    status_code: int,
    message: str,
) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status_code,
        content={
            "response": "error",
            "message": _(message),
        },
    )


def bad_request(message: str) -> ORJSONResponse:
    return error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        message=message,
    )


def not_found(message: str = "Resource not found") -> ORJSONResponse:
    return error_response(
        status_code=status.HTTP_404_NOT_FOUND,
        message=message,
    )


def success_response(
    data: dict,
    status_code: int = status.HTTP_200_OK,
) -> ORJSONResponse:
    content = {"response": "ok"}
    content.update(data)
    return ORJSONResponse(
        status_code=status_code,
        content=content,
    )
