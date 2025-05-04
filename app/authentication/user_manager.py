import logging
import re
from typing import TYPE_CHECKING, Optional, Union

from fastapi_users import (BaseUserManager, IntegerIDMixin,
                           InvalidPasswordException)

from app.core.config import settings
from app.core.types.user_id import UserIdType
from app.users.models import User
from app.users.schemas import UserCreate
from app.utils.webhooks.user import send_new_user_notification

if TYPE_CHECKING:
    from fastapi import Request


log = logging.getLogger(__name__)


class UserManager(IntegerIDMixin, BaseUserManager[User, UserIdType]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:

        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )

        if not re.search(r"[!@#$%^&*()_\-+={}[\]|\\:;\'<>?,./]", password):
            raise InvalidPasswordException(
                reason="Password should contain at least one special character"
            )

        if not re.search(r"[A-Z]", password):
            raise InvalidPasswordException(
                reason="Password should contain at least one capital letter"
            )

        if not re.search(r"[0-9]", password):
            raise InvalidPasswordException(
                reason="Password should contain at least one digit"
            )

        if user.email in password:
            raise InvalidPasswordException(reason="Password should not contain e-mail")

    async def on_after_register(self, user: User, request: Optional["Request"] = None):
        log.warning("User %r has registered.", user.id)

        await send_new_user_notification(user)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional["Request"] = None
    ):
        log.warning(
            "User %r has forgot their password. Reset token: %r", user.id, token
        )

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional["Request"] = None
    ):
        log.warning(
            "Verification requested for user %r. Verification token: %r", user.id, token
        )
