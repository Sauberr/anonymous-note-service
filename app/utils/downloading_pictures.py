import os
import shutil
import uuid_utils as uuid
from fastapi import UploadFile


async def download_image(
    image: UploadFile, upload_dir: str = "app/static/images"
) -> str:
    if image is None:
        raise ValueError("No image file provided")

    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)

    file_extension = os.path.splitext(image.filename or "")[1]
    image_name = f"{uuid.uuid4().hex}{file_extension}"
    saved_path = os.path.join(upload_dir, image_name)

    with open(saved_path, "wb") as file_object:
        shutil.copyfileobj(image.file, file_object)

    return image_name
