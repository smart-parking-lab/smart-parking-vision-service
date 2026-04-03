import requests
import cv2
import numpy as np
import time
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("camera_service")

IP_CAMERA = os.getenv("IP_CAMERA", "192.168.1.41")
CAMERA_PORT = os.getenv("CAMERA_PORT", "8080")
URL_FOCUS = f"http://{IP_CAMERA}:{CAMERA_PORT}/focus"
URL_SHOT = f"http://{IP_CAMERA}:{CAMERA_PORT}/shot.jpg"


def capture_image_from_camera() -> bytes | None:
    """
    Chụp ảnh từ camera IP (IP Webcam app trên Android).
    Trả về image bytes nếu thành công, None nếu thất bại.
    """
    try:
        # Ép camera lấy nét (autofocus)
        logger.info("📸 Đang ép camera lấy nét...")
        try:
            requests.get(URL_FOCUS, timeout=2)
        except requests.Timeout:
            logger.warning("⚠️ Timeout khi ép lấy nét, tiếp tục chụp...")

        # Chờ thấu kính ổn định
        time.sleep(0.6)

        # Tải ảnh snapshot
        logger.info(f"📸 Đang chụp ảnh từ camera ({URL_SHOT})...")
        response = requests.get(URL_SHOT, timeout=5)

        if response.status_code == 200:
            logger.info(f"✅ Đã chụp ảnh thành công ({len(response.content)} bytes)")
            return response.content
        else:
            logger.error(f"❌ Camera trả về HTTP {response.status_code}")
            return _fallback_local_image()

    except requests.ConnectionError:
        logger.error(f"❌ Không thể kết nối camera tại {IP_CAMERA}:{CAMERA_PORT}")
        logger.info("⚠️ Đang kích hoạt FALLBACK (sử dụng ảnh test-images/image8.jpg)")
        return _fallback_local_image()
    except Exception as e:
        logger.error(f"❌ Lỗi chụp ảnh: {e}")
        return _fallback_local_image()

def _fallback_local_image() -> bytes | None:
    """Đọc ảnh từ đĩa cứng khi không có camera để test luồng LPR"""
    try:
        with open("test-images/image8.jpg", "rb") as f:
            return f.read()
    except FileNotFoundError:
        logger.error("❌ Không tìm thấy ảnh test fallback")
        return None


def image_bytes_to_opencv_frame(image_bytes: bytes):
    """Chuyển raw bytes thành OpenCV frame (numpy array)."""
    image_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return frame
