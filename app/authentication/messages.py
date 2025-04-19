from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.dependencies.fastapi_users import current_active_superuser, current_active_user
from app.users.models import User
from app.users.schemas import UserRead

router = APIRouter(
    prefix=settings.api.v1.messages,
    tags=["Messages"],
)


@router.get("/error")
def view_may_raise_error(
    raise_error: bool = False,
):
    if raise_error:
        UserRead.model_validate(None)
    return {"ok": True}


@router.get("")
def get_user_messages(
    user: Annotated[User, Depends(current_active_user)],
):
    return {
        "messages": ["message1", "message2"],
        "user": UserRead.model_validate(user),
    }


@router.get("/secrets")
def get_superuser_messages(
    user: Annotated[User, Depends(current_active_superuser)],
):
    return {
        "messages": ["secret-message1", "secret-message2"],
        "user": UserRead.model_validate(user),
    }
