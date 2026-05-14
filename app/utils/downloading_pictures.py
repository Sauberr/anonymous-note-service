import asyncio
import os
from pathlib import Path

import uuid_utils as uuid
from fastapi import UploadFile


async def download_image(
    image: UploadFile, upload_dir: str = Path("app/static/images").absolute()
) -> str:
    if image is None:
        raise ValueError("No image file provided")

    os.makedirs(upload_dir, exist_ok=True)

    file_extension = os.path.splitext(image.filename or "")[1]
    image_name = f"{uuid.uuid4().hex}{file_extension}"
    saved_path = os.path.join(upload_dir, image_name)

    contents = await image.read()
    await asyncio.to_thread(Path(saved_path).write_bytes, contents)

    return image_name
