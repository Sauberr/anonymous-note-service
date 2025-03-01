from datetime import datetime, timedelta, timezone
from secrets import compare_digest

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette.responses import JSONResponse

from fastapi import status
from app.notes.services import get_note_id
from app.notes.models import NoteORM
from app.utils import (download_image, get_async_session)
from app.notes.services import is_lifetime_note, is_ephemeral_note


note_router = APIRouter(
    tags=["Note"],
)

templates = Jinja2Templates(directory="app/templates")


@note_router.get("/", response_class=HTMLResponse)
async def get_home_page(request: Request, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(NoteORM))
    notes = result.scalars().all()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "notes_count": len(notes)
    })


@note_router.post("/create_note")
async def create_note(
    db: AsyncSession = Depends(get_async_session),
    secret: str = Form(...),
    text: str = Form(...),
    lifetime_hours: int = Form(0),
    lifetime_minutes: int = Form(0),
    lifetime_seconds: int = Form(0),
    is_ephemeral: bool = Form(False),
    image: UploadFile = File(None)
) -> JSONResponse:
    if is_ephemeral and (lifetime_hours > 0 or lifetime_minutes > 0 or lifetime_seconds > 0):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"response": "error", "error": "Ephemeral notes cannot have a lifetime"}
        )

    lifetime = None
    if not is_ephemeral:
        total_seconds = lifetime_hours * 3600 + lifetime_minutes * 60 + lifetime_seconds
        if total_seconds > 0:
            lifetime = datetime.now(timezone.utc) + timedelta(seconds=total_seconds)

    note_id = get_note_id(text=text, salt=secret)

    saved_filename = await download_image(image) if image else None

    note = NoteORM(
        text=text,
        secret=secret,
        note_hash=note_id,
        is_ephemeral=is_ephemeral,
        lifetime=lifetime,
        image=saved_filename
    )
    db.add(note)
    await db.commit()

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"response": "ok", "note_id": note_id}
    )


@note_router.get("/result/{note_id}", response_class=HTMLResponse)
async def get_result_id(request: Request, note_id: str):
    return templates.TemplateResponse("hash_storage.html", {
        "request": request,
        "note_id": note_id
    })


@note_router.post("/get_note")
async def get_note(
        db: AsyncSession = Depends(get_async_session),
        note_id: str = Form(...),
        note_secret: str = Form(...)
) -> JSONResponse:
    result = await db.execute(select(NoteORM).where(NoteORM.note_hash == note_id))
    note = result.scalar_one_or_none()

    if note and compare_digest(str(note.secret), str(note_secret)):
        if await is_lifetime_note(note, db):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"response": "error", "note_final_text": "Such a note does not exist"}
            )

        note_text = note.text
        note_image = note.image or ""

        is_ephemeral = await is_ephemeral_note(note, db)

        return JSONResponse(
            content={
                "response": "ok",
                "note_final_text": note_text,
                "note_image": note_image
            }
        )
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"response": "error", "note_final_text": "Such a note does not exist"}
    )


@note_router.get("/note_page/{note_text}", response_class=HTMLResponse)
async def get_result_note(request: Request, note_text: str, note_image: str = ""):
    return templates.TemplateResponse("note_page.html", {
        "request": request,
        "note_text": note_text,
        "note_image": note_image
    })


@note_router.get("/notes", response_class=JSONResponse)
async def get_notes(
    db: AsyncSession = Depends(get_async_session),
    page: int = Query(1, ge=1),
    per_page: int = Query(3, ge=1, le=100)
) -> JSONResponse:
    offset = (page - 1) * per_page
    result = await db.execute(select(NoteORM).offset(offset).limit(per_page))
    notes = result.scalars().all()
    notes_data = [{"id": note.id,
                   "text": note.text,
                   "image": note.image if hasattr(note, 'image') else None} for note in notes]
    return JSONResponse(content={"notes": notes_data, "page": page, "per_page": per_page, "total": len(notes)})
