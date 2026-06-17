import os
import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from app.services.lpr_service import (
    capture_image_from_camera,
    load_image_from_path,
    recognize_plate,
)
from app.services.storage_service import (
    save_image,
    generate_cloudinary_url,
    save_image_in_background,
)
from app.core.config import IMAGE_DIR
from app.utils.logger import get_logger

logger = get_logger("api_recognize")

router = APIRouter(prefix="/recognize", tags=["Nhận diện biển số"])


class LocalImageRequest(BaseModel):
    """Request body cho API nhận diện từ ảnh local."""
    file_path: str | None = None
    file_name: str | None = None


@router.post("/camera")
async def recognize_from_camera(background_tasks: BackgroundTasks):
    """
    API 1: Gọi trực tiếp đến camera chụp ảnh → nhận diện biển số.
    Ảnh được sinh trước URL Cloudinary/local và lưu chạy ngầm.
    """
    img, raw_bytes = await capture_image_from_camera()
    if img is None:
        raise HTTPException(status_code=502, detail="Không thể chụp ảnh từ camera")

    plate = recognize_plate(img)

    image_uuid = str(uuid.uuid4())
    image_url = generate_cloudinary_url(image_uuid)

    background_tasks.add_task(save_image_in_background, raw_bytes, image_uuid)

    return {
        "plate": plate,
        "image_url": image_url,
    }


@router.post("/local")
async def recognize_from_local(payload: LocalImageRequest, background_tasks: BackgroundTasks):
    """
    API 2: Lấy ảnh từ local trong máy để nhận diện biển số.
    Truyền file_path (đường dẫn tuyệt đối) hoặc file_name (tên file trong thư mục IMAGE_DIR).
    """
    if payload.file_path:
        file_path = payload.file_path
    elif payload.file_name:
        file_path = os.path.join(IMAGE_DIR, payload.file_name)
    else:
        raise HTTPException(
            status_code=400,
            detail="Phải truyền file_path hoặc file_name",
        )

    img, raw_bytes = load_image_from_path(file_path)
    if img is None:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy hoặc không đọc được ảnh: {file_path}",
        )

    plate = recognize_plate(img)

    image_uuid = str(uuid.uuid4())
    image_url = generate_cloudinary_url(image_uuid)

    background_tasks.add_task(save_image_in_background, raw_bytes, image_uuid)

    return {
        "plate": plate,
        "image_url": image_url,
    }
