import uuid

import pytest
from pydantic import ValidationError

from app.users.schemas import (
    UserCreate,
    UserRead,
    UserRegisteredNotification,
    UserUpdate,
)
from app.utils.case_converter import camel_case_to_snake_case



def test_user_create_requires_valid_email():
    """UserCreate rejects malformed emails and accepts valid ones."""

    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email", password="secret123")

    user = UserCreate(email="alice@example.com", password="secret123")
    assert user.email == "alice@example.com"
    assert user.password == "secret123"


def test_user_read_exposes_public_fields_only():
    """UserRead serialises identity/status flags but never the password."""

    uid = uuid.uuid4()
    user = UserRead(
        id=uid,
        email="bob@example.com",
        is_active=True,
        is_superuser=False,
        is_verified=False,
    )

    dumped = user.model_dump()
    assert dumped["email"] == "bob@example.com"
    assert dumped["is_active"] is True
    assert "password" not in dumped
    assert "hashed_password" not in dumped


def test_user_update_is_all_optional():
    """UserUpdate allows partial updates with no required fields."""

    empty = UserUpdate()
    assert empty.model_dump(exclude_unset=True) == {}

    partial = UserUpdate(password="new-password")
    assert partial.password == "new-password"


def test_user_registered_notification_shape():
    """The webhook notification carries a UserRead payload plus a timestamp."""

    payload = UserRegisteredNotification(
        user=UserRead(
            id=uuid.uuid4(),
            email="carol@example.com",
            is_active=True,
            is_superuser=False,
            is_verified=True,
        ),
        ts=1_700_000_000,
    )

    assert payload.ts == 1_700_000_000
    assert payload.user.email == "carol@example.com"


# ---- utility tests ----------------------------------------------------------


@pytest.mark.parametrize(
    "given, expected",
    [
        ("SomeSDK", "some_sdk"),
        ("RServer", "r_server"),
        ("SomeClass", "some_class"),
        ("HTTPResponse", "http_response"),
        ("User", "user"),
    ],
)
def test_camel_case_to_snake_case(given, expected):
    """Table names / identifiers convert CamelCase to snake_case correctly."""

    assert camel_case_to_snake_case(given) == expected
