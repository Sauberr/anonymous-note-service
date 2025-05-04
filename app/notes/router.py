from datetime import datetime, timedelta, timezone
from secrets import compare_digest

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi_babel import _
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.models.db_helper import db_helper
from app.core.templates import templates
from app.errors_handlers import bad_request, not_found, success_response
from app.notes.models import Note
from app.notes.services import get_note_id, is_ephemeral_note, is_lifetime_note
from app.utils.downloading_pictures import download_image
from app.schemas.common import MessageErrorSchema

router = APIRouter(
    tags=["Note"],
    prefix=settings.api.v1.notes,
)


@router.get(
    "/",
    response_class=HTMLResponse,
    summary="Main page",
    response_description="Main page with the number of notes",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": MessageErrorSchema, "description": "Bad request"},
    },
)
async def get_home_page(
    request: Request, db: AsyncSession = Depends(db_helper.session_getter)
):
    result = await db.execute(select(Note))
    notes = result.scalars().all()
    return templates.TemplateResponse(
        request, "index.html", {"notes_count": len(notes)}
    )


@router.post(
    "/create_note",
    summary="Create a note",
    response_description="Create a note",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": MessageErrorSchema, "description": "Bad request"},
        404: {"model": MessageErrorSchema, "description": "Not found"},
    },
)
async def create_note(
    db: AsyncSession = Depends(db_helper.session_getter),
    secret: str = Form(...),
    text: str = Form(...),
    lifetime_hours: int = Form(0),
    lifetime_minutes: int = Form(0),
    lifetime_seconds: int = Form(0),
    is_ephemeral: bool = Form(False),
    image: UploadFile = File(None),
) -> ORJSONResponse:
    if is_ephemeral and (
        lifetime_hours > 0 or lifetime_minutes > 0 or lifetime_seconds > 0
    ):
        return bad_request(_("Ephemeral notes cannot have a lifetime"))

    lifetime = None
    seconds_in_hour: int = 3600
    seconds_in_minute: int = 60

    if not is_ephemeral:
        total_seconds = (
            lifetime_hours * seconds_in_hour
            + lifetime_minutes * seconds_in_minute
            + lifetime_seconds
        )
        if total_seconds > 0:
            lifetime = datetime.now(timezone.utc) + timedelta(seconds=total_seconds)

    note_id = get_note_id(text=text, salt=secret)

    saved_filename = await download_image(image) if image else None

    note = Note(
        text=text,
        secret=secret,
        note_hash=note_id,
        is_ephemeral=is_ephemeral,
        lifetime=lifetime,
        image=saved_filename,
    )
    db.add(note)
    await db.commit()

    return success_response({"note_id": note_id})


@router.get(
    "/result/{note_id}",
    response_class=HTMLResponse,
    summary="Get result page",
    response_description="Get result page",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": MessageErrorSchema, "description": "Bad request"},
        404: {"model": MessageErrorSchema, "description": "Not found"},
    },
)
async def get_result_id(request: Request, note_id: str):
    return templates.TemplateResponse(
        request, "hash_storage.html", {"note_id": note_id}
    )


@router.post(
    "/get_note",
    summary="Get a note",
    response_description="Get a note",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": MessageErrorSchema, "description": "Bad request"},
        404: {"model": MessageErrorSchema, "description": "Not found"},
    },
)
async def get_note(
    db: AsyncSession = Depends(db_helper.session_getter),
    note_id: str = Form(...),
    note_secret: str = Form(...),
) -> ORJSONResponse:
    result = await db.execute(select(Note).where(Note.note_hash == note_id))
    note = result.scalar_one_or_none()

    if note and compare_digest(str(note.secret), str(note_secret)):
        if await is_lifetime_note(note, db):
            return not_found(_("Such a note does not exist"))

        note_text = note.text
        note_image = note.image or ""

        is_ephemeral = await is_ephemeral_note(note, db)

        return success_response(
            {
                "note_final_text": note_text,
                "note_image": note_image,
            }
        )
    return not_found(_("Such a note does not exist"))


@router.get(
    "/note_page/{note_text}",
    response_class=HTMLResponse,
    summary="Get the current content of the note",
    response_description="Get the current content of the note",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": MessageErrorSchema, "description": "Bad request"},
        404: {"model": MessageErrorSchema, "description": "Not found"},
    },
)
async def get_result_note(request: Request, note_text: str, note_image: str = ""):
    return templates.TemplateResponse(
        request,
        "note_page.html",
        {"note_text": note_text, "note_image": note_image},
    )


@router.get(
    "/notes",
    response_class=ORJSONResponse,
    summary="Paginated notes",
    response_description="Paginated notes",
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": MessageErrorSchema, "description": "Bad request"},
        404: {"model": MessageErrorSchema, "description": "Not found"},
    },
)
async def get_notes(
    db: AsyncSession = Depends(db_helper.session_getter),
    page: int = Query(1, ge=1),
    per_page: int = Query(3, ge=1, le=100),
) -> ORJSONResponse:
    offset = (page - 1) * per_page
    result = await db.execute(select(Note).offset(offset).limit(per_page))
    notes = result.scalars().all()
    notes_data = [
        {
            "id": note.id,
            "text": note.text,
            "image": note.image if hasattr(note, "image") else None,
        }
        for note in notes
    ]
    return success_response(
        {
            "notes": notes_data,
            "page": page,
            "per_page": per_page,
            "total_notes": len(notes),
        }
    )
