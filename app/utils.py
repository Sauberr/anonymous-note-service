import os
import shutil
from sqlalchemy.ext.asyncio import AsyncSession

import uuid_utils as uuid
from fastapi import UploadFile
from collections.abc import AsyncGenerator

from app.db_session import async_session_maker


def camel_case_to_snake_case(input_str: str) -> str:
    chars = []
    for c_idx, char in enumerate(input_str):
        if c_idx and char.isupper():
            nxt_idx = c_idx + 1
            flag = nxt_idx >= len(input_str) or input_str[nxt_idx].isupper()
            prev_char = input_str[c_idx - 1]
            if prev_char.isupper() and flag:
                pass
            else:
                chars.append("_")
        chars.append(char.lower())
    return "".join(chars)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def download_image(image: UploadFile, upload_dir: str = "app/static/images") -> str:
    if image is None:
        raise ValueError("No image file provided")

    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)

    file_extension = os.path.splitext(image.filename or "")[1]
    unique_name = f"{uuid.uuid4().hex}{file_extension}"
    saved_path = os.path.join(upload_dir, unique_name)

    with open(saved_path, "wb") as file_object:
        shutil.copyfileobj(image.file, file_object)

    return unique_name