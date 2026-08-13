import io
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.notes.models import Note
from app.notes.services import (
    delete_expired_notes,
    get_note_id,
    is_ephemeral_note,
    is_lifetime_note,
)
from app.utils.downloading_pictures import download_image


def _make_session():
    """Build a mock async session usable as an async generator source."""

    session = AsyncMock(spec=AsyncSession)
    session.delete = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session


def _helper_yielding(session):
    """Return an object whose session_getter yields the given session once."""

    helper = MagicMock()

    async def _gen():
        yield session

    helper.session_getter = _gen
    return helper


@pytest.mark.asyncio
async def test_get_note_id_is_sha256_hex():
    """get_note_id returns a deterministic 64-char sha256 hex digest."""

    note_id = get_note_id(text="hello", salt="salt")

    assert len(note_id) == 64
    assert all(c in "0123456789abcdef" for c in note_id)
    # different text -> different id
    assert note_id != get_note_id(text="hello!", salt="salt")


@pytest.mark.asyncio
async def test_is_lifetime_note_future_keeps_note():
    """A note whose lifetime is in the future is not deleted."""

    note = Note(lifetime=datetime.now(timezone.utc) + timedelta(hours=2))
    session = _make_session()

    assert await is_lifetime_note(note, session) is False
    session.delete.assert_not_called()


@pytest.mark.asyncio
async def test_is_lifetime_note_expired_deletes():
    """An expired note is deleted and committed."""

    note = Note(lifetime=datetime.now(timezone.utc) - timedelta(seconds=1))
    session = _make_session()

    assert await is_lifetime_note(note, session) is True
    session.delete.assert_awaited_once_with(note)
    session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_is_ephemeral_note_deletes_when_ephemeral():
    """Ephemeral notes are removed after access; regular notes are kept."""

    session = _make_session()

    assert await is_ephemeral_note(Note(is_ephemeral=True), session) is True
    assert await is_ephemeral_note(Note(is_ephemeral=False), session) is False
    session.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_expired_notes_removes_all_matches():
    """delete_expired_notes deletes every expired row and commits once."""

    expired = [Note(id=1, lifetime=datetime.now(timezone.utc) - timedelta(hours=1)),
               Note(id=2, lifetime=datetime.now(timezone.utc) - timedelta(hours=3))]

    result = MagicMock()
    result.scalars.return_value.all.return_value = expired

    session = _make_session()
    session.execute = AsyncMock(return_value=result)

    await delete_expired_notes(_helper_yielding(session))

    assert session.delete.await_count == 2
    session.commit.assert_awaited_once()
    session.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_delete_expired_notes_rolls_back_on_error():
    """A failure during processing triggers rollback and re-raises."""

    session = _make_session()
    session.execute = AsyncMock(side_effect=RuntimeError("db down"))

    with pytest.raises(RuntimeError, match="db down"):
        await delete_expired_notes(_helper_yielding(session))

    session.rollback.assert_awaited_once()
    session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_download_image_returns_unique_name(tmp_path):
    """download_image writes bytes and returns a uuid-based filename."""

    upload = UploadFile(filename="photo.png", file=io.BytesIO(b"binary-bytes"))

    name = await download_image(upload, upload_dir=str(tmp_path))

    assert name.endswith(".png")
    assert (tmp_path / name).read_bytes() == b"binary-bytes"


@pytest.mark.asyncio
async def test_download_image_none_raises():
    """Passing no image raises ValueError."""

    with pytest.raises(ValueError, match="No image file provided"):
        await download_image(None, upload_dir="/tmp")
