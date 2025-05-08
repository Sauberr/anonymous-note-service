import io
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi import status
from pytest_asyncio import fixture
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.db_helper import db_helper
from app.main import main_app
from app.notes.models import Note
from app.notes.services import get_note_id


BASE_URL: str = "/api/v1/notes"
NOTE_URL: str = f"{BASE_URL}/get_note"
CREATE_NOTE_URL: str = f"{BASE_URL}/create_note"
NOTES_LIST_URL: str = f"{BASE_URL}/notes/"
HOME_URL: str = f"{BASE_URL}/"
RESULT_URL: str = f"{BASE_URL}/result/"
NOTE_PAGE_URL: str = f"{BASE_URL}/note_page/"


@pytest.fixture
def client():
    """Create a test client for the app."""

    return TestClient(main_app)


@fixture
async def mock_db():
    """Create a mock async session for database operations."""

    mock_session = AsyncMock(spec=AsyncSession)

    mock_result = MagicMock()
    mock_session.execute.return_value = mock_result

    return mock_session


@fixture
async def mock_db_dependency(mock_db):
    """Override the database dependency for testing."""

    main_app.dependency_overrides[db_helper.session_getter] = lambda: mock_db
    yield
    main_app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_note(client, mock_db, mock_db_dependency):
    """Test creating a regular note."""

    mock_db.commit = AsyncMock()

    response = client.post(
        CREATE_NOTE_URL,
        data={
            "secret": "test_secret",
            "text": "This is a test note",
            "lifetime_hours": 0,
            "lifetime_minutes": 0,
            "lifetime_seconds": 0,
            "is_ephemeral": False,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert "note_id" in response.json()

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_note_with_image(client, mock_db, mock_db_dependency):
    """Test creating a note with an image upload."""

    mock_db.commit = AsyncMock()
    image_data = io.BytesIO(b"fake-image-content")
    image_file = ("file", ("test_image.png", image_data, "image/png"))

    with patch("app.notes.router") as mock_uuid:
        mock_uuid.return_value.hex = "fakeuuid"
        response = client.post(
            CREATE_NOTE_URL,
            data={
                "secret": "test_secret",
                "text": "Note with image",
                "lifetime_hours": 0,
                "lifetime_minutes": 0,
                "lifetime_seconds": 0,
                "is_ephemeral": False,
            },
            files={"image": ("test_image.png", image_data, "image/png")},
        )

    assert response.status_code == status.HTTP_200_OK
    assert "note_id" in response.json()

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    args, _ = mock_db.add.call_args
    note_obj = args[0]
    assert hasattr(note_obj, "image")
    assert note_obj.image is not None


@pytest.mark.asyncio
async def test_create_ephemeral_note(client, mock_db, mock_db_dependency):
    """Test creating an ephemeral note."""

    mock_db.commit = AsyncMock()

    response = client.post(
        CREATE_NOTE_URL,
        data={
            "secret": "test_secret",
            "text": "This is an ephemeral note",
            "lifetime_hours": 0,
            "lifetime_minutes": 0,
            "lifetime_seconds": 0,
            "is_ephemeral": True,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert "note_id" in response.json()

    mock_db.add.assert_called_once()
    args, kwargs = mock_db.add.call_args
    assert args[0].is_ephemeral is True
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_lifetime_note(client, mock_db, mock_db_dependency):
    """Test creating a note with lifetime."""

    mock_db.commit = AsyncMock()

    response = client.post(
        CREATE_NOTE_URL,
        data={
            "secret": "test_secret",
            "text": "This is a lifetime note",
            "lifetime_hours": 1,
            "lifetime_minutes": 30,
            "lifetime_seconds": 0,
            "is_ephemeral": False,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert "note_id" in response.json()

    mock_db.add.assert_called_once()
    args, kwargs = mock_db.add.call_args
    assert args[0].lifetime is not None
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_create_ephemeral_note_with_lifetime_error(
    client, mock_db, mock_db_dependency
):
    """Test error when trying to create an ephemeral note with a lifetime."""

    response = client.post(
        CREATE_NOTE_URL,
        data={
            "secret": "test_secret",
            "text": "This shouldn't work",
            "lifetime_hours": 1,
            "lifetime_minutes": 0,
            "lifetime_seconds": 0,
            "is_ephemeral": True,
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ephemeral notes cannot have a lifetime" in response.json()["message"]

    mock_db.add.assert_not_called()


@pytest.mark.asyncio
async def test_get_note(client, mock_db, mock_db_dependency):
    """Test getting a note with valid ID and secret."""

    note_id = "test_note_id"
    note_secret = "test_secret"
    note_text = "This is a test note"

    mock_note = Note(
        text=note_text,
        secret=note_secret,
        note_hash=note_id,
        is_ephemeral=False,
        lifetime=None,
        image=None,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_note
    mock_db.execute.return_value = mock_result

    with (
        patch(
            "app.notes.router.is_lifetime_note", return_value=False
        ) as mock_lifetime,
        patch(
            "app.notes.router.is_ephemeral_note", return_value=False
        ) as mock_ephemeral,
    ):
        response = client.post(
            NOTE_URL,
            data={"note_id": note_id, "note_secret": note_secret},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["note_final_text"] == note_text

        mock_db.execute.assert_called_once()
        mock_lifetime.assert_called_once_with(mock_note, mock_db)
        mock_ephemeral.assert_called_once_with(mock_note, mock_db)


@pytest.mark.asyncio
async def test_get_note_expired_lifetime(client, mock_db, mock_db_dependency):
    """Test getting a note with an expired lifetime."""

    note_id = "test_note_id"
    note_secret = "test_secret"

    mock_note = Note(
        text="This is an expired note",
        secret=note_secret,
        note_hash=note_id,
        is_ephemeral=False,
        lifetime=datetime.now(timezone.utc) - timedelta(hours=1),
        image=None,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_note
    mock_db.execute.return_value = mock_result

    with patch("app.notes.services.is_lifetime_note", return_value=True):
        response = client.post(
            NOTE_URL,
            data={"note_id": note_id, "note_secret": note_secret},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Such a note does not exist" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_note_wrong_secret(client, mock_db, mock_db_dependency):
    """Test getting a note with an incorrect secret."""

    note_id = "test_note_id"
    note_secret = "test_secret"
    wrong_secret = "wrong_secret"

    mock_note = Note(
        text="This is a protected note",
        secret=note_secret,
        note_hash=note_id,
        is_ephemeral=False,
        lifetime=None,
        image=None,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_note
    mock_db.execute.return_value = mock_result

    response = client.post(
        NOTE_URL,
        data={"note_id": note_id, "note_secret": wrong_secret},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Such a note does not exist" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_notes_pagination(client, mock_db, mock_db_dependency):
    """Test getting notes with pagination."""

    mock_notes = [
        Note(id=1, text="Note 1", image=None),
        Note(id=2, text="Note 2", image="image2.png"),
        Note(id=3, text="Note 3", image=None),
    ]

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = mock_notes
    mock_db.execute.return_value = mock_result

    response = client.get(f"{NOTES_LIST_URL}?page=1&per_page=3")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["page"] == 1
    assert data["per_page"] == 3
    assert data["total_notes"] == 3
    assert len(data["notes"]) == 3

    for i, note in enumerate(data["notes"]):
        assert note["id"] == mock_notes[i].id
        assert note["text"] == mock_notes[i].text
        assert note["image"] == mock_notes[i].image


@pytest.mark.asyncio
async def test_get_ephemeral_note(client, mock_db, mock_db_dependency):
    """Test getting an ephemeral note that will be deleted after access."""

    note_id = "test_ephemeral_id"
    note_secret = "test_secret"
    note_text = "This is an ephemeral note"

    mock_note = Note(
        text=note_text,
        secret=note_secret,
        note_hash=note_id,
        is_ephemeral=True,
        lifetime=None,
        image=None,
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_note
    mock_db.execute.return_value = mock_result

    with (
        patch(
            "app.notes.router.is_lifetime_note", return_value=False
        ) as mock_lifetime,
        patch(
            "app.notes.router.is_ephemeral_note", return_value=True
        ) as mock_ephemeral,
    ):
        response = client.post(
            NOTE_URL,
            data={"note_id": note_id, "note_secret": note_secret},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["note_final_text"] == note_text

        mock_db.execute.assert_called_once()
        mock_lifetime.assert_called_once_with(mock_note, mock_db)
        mock_ephemeral.assert_called_once_with(mock_note, mock_db)


@pytest.mark.asyncio
async def test_get_note_not_found(client, mock_db, mock_db_dependency):
    """Test getting a note that doesn't exist."""

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    response = client.post(
        NOTE_URL,
        data={"note_id": "nonexistent_id", "note_secret": "secret"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Such a note does not exist" in response.json()["message"]


@pytest.mark.asyncio
async def test_get_home_page(client, mock_db, mock_db_dependency):
    """Test the home page loads with the correct note count."""

    mock_notes = [Note(id=i, text=f"Note {i}") for i in range(5)]

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = mock_notes
    mock_db.execute.return_value = mock_result

    response = client.get(BASE_URL)

    assert response.status_code == status.HTTP_200_OK
    assert b"!DOCTYPE html" in response.content

    mock_db.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_result_id_page(client):
    """Test the result ID page loads correctly."""

    note_id = "test_note_id"

    response = client.get(f"{RESULT_URL}{note_id}")

    assert response.status_code == status.HTTP_200_OK
    assert b"hash_storage.html" in response.content or b"note_id" in response.content


@pytest.mark.asyncio
async def test_get_note_page(client):
    """Test the note page loads correctly."""

    note_text = "This is a test note"
    note_image = "test_image.png"

    response = client.get(
        f"{NOTE_PAGE_URL}{note_text}?note_image={note_image}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert (
        b"note_page.html" in response.content or note_text.encode() in response.content
    )


# Tests for helper functions and services


@pytest.mark.asyncio
async def test_get_note_id():
    """Test the get_note_id function to ensure it generates deterministic IDs."""

    text = "Test note"
    salt = "test_salt"

    id1 = get_note_id(text=text, salt=salt)
    id2 = get_note_id(text=text, salt=salt)

    assert id1 == id2

    id3 = get_note_id(text=text, salt="different_salt")

    assert id1 != id3


@pytest.mark.asyncio
async def test_is_lifetime_note():
    """Test the is_lifetime_note function."""

    from app.notes.services import is_lifetime_note

    future_note = Note(lifetime=datetime.now(timezone.utc) + timedelta(hours=1))

    past_note = Note(lifetime=datetime.now(timezone.utc) - timedelta(hours=1))

    no_lifetime_note = Note(lifetime=None)

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.delete = AsyncMock()
    mock_db.commit = AsyncMock()

    assert await is_lifetime_note(future_note, mock_db) is False
    assert await is_lifetime_note(past_note, mock_db) is True
    assert await is_lifetime_note(no_lifetime_note, mock_db) is False

    mock_db.delete.assert_called_once_with(past_note)
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_is_ephemeral_note():
    """Test the is_ephemeral_note function."""

    from app.notes.services import is_ephemeral_note

    ephemeral_note = Note(is_ephemeral=True)

    regular_note = Note(
        is_ephemeral=False
    )

    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.delete = AsyncMock()
    mock_db.commit = AsyncMock()

    assert await is_ephemeral_note(ephemeral_note, mock_db) is True
    assert await is_ephemeral_note(regular_note, mock_db) is False

    mock_db.delete.assert_called_once_with(ephemeral_note)
    mock_db.commit.assert_called_once()
