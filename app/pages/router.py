from fastapi import APIRouter, Request, status
from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.core.templates import templates

router = APIRouter(
    tags=["Pages"],
    prefix=settings.api.v1.account,
)


@router.get(
    "/",
    response_class=HTMLResponse,
    summary="Account page",
    response_description="Sign in / sign up / reset password page",
    status_code=status.HTTP_200_OK,
)
async def account_page(request: Request):
    return templates.TemplateResponse(
        request,
        "auth.html",
        {"locale": request.cookies.get("locale", "en")},
    )
