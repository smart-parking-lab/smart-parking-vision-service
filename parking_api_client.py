import requests
import logging
import os
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

logger = logging.getLogger("parking_api_client")

DASHBOARD_BASE_URL = os.getenv("DASHBOARD_API_URL", "http://127.0.0.1:9000")
PARKING_SESSIONS_ENDPOINT = f"{DASHBOARD_BASE_URL}/api/v1/parking-sessions"
INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")

REQUEST_TIMEOUT = 15


def _build_headers() -> dict:
    """Tạo headers chung cho mọi request, bao gồm API key nội bộ."""
    headers = {}
    if INTERNAL_API_KEY:
        headers["X-Internal-Key"] = INTERNAL_API_KEY
    return headers


def create_parking_session(plate_number: str, image_bytes: bytes) -> dict | None:
    """
    Gọi POST /api/v1/parking-sessions để tạo phiên đỗ xe (xe vào).
    Dashboard yêu cầu multipart/form-data với plate_number (Form) + entry_image (File).
    """
    try:
        files = {
            "entry_image": ("entry.jpg", BytesIO(image_bytes), "image/jpeg"),
        }
        data = {
            "plate_number": plate_number,
        }

        response = requests.post(
            PARKING_SESSIONS_ENDPOINT,
            data=data,
            files=files,
            headers=_build_headers(),
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 201:
            result = response.json()
            logger.info(f"✅ Dashboard đã tạo phiên đỗ xe cho {plate_number}")
            return result
        else:
            logger.error(
                f"❌ Dashboard trả về HTTP {response.status_code}: {response.text}"
            )
            return None

    except requests.ConnectionError:
        logger.error(f"❌ Không thể kết nối tới Dashboard tại {DASHBOARD_BASE_URL}")
        return None
    except requests.Timeout:
        logger.error("❌ Timeout khi gọi Dashboard API")
        return None
    except Exception as e:
        logger.error(f"❌ Lỗi khi gọi create_parking_session API: {e}")
        return None


def update_parking_session(plate_number: str, image_bytes: bytes) -> dict | None:
    """
    Gọi PUT /api/v1/parking-sessions để cập nhật phiên đỗ xe (xe ra).
    Dashboard yêu cầu multipart/form-data với plate_number (Form) + exit_image (File).
    """
    try:
        files = {
            "exit_image": ("exit.jpg", BytesIO(image_bytes), "image/jpeg"),
        }
        data = {
            "plate_number": plate_number,
        }

        response = requests.put(
            PARKING_SESSIONS_ENDPOINT,
            data=data,
            files=files,
            headers=_build_headers(),
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Dashboard đã cập nhật phiên đỗ xe cho {plate_number}")
            return result
        else:
            logger.error(
                f"❌ Dashboard trả về HTTP {response.status_code}: {response.text}"
            )
            return None

    except requests.ConnectionError:
        logger.error(f"❌ Không thể kết nối tới Dashboard tại {DASHBOARD_BASE_URL}")
        return None
    except requests.Timeout:
        logger.error("❌ Timeout khi gọi Dashboard API")
        return None
    except Exception as e:
        logger.error(f"❌ Lỗi khi gọi update_parking_session API: {e}")
        return None
