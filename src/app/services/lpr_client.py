import httpx
from app.core.config import LPR_SERVICE_URL
from app.utils.logger import get_logger

logger = get_logger("lpr_client")

async def recognize_plate(gate: str) -> dict | None:
    """
    Gọi API 'bên kia' (LPR Service) để nhận diện biển số.
    """
    url = f"{LPR_SERVICE_URL}/recognize"
    payload = {"gate": gate}

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(url, json=payload)

        if response.status_code == 200:
            return response.json()
            
        logger.error(f"❌ LPR Service lỗi HTTP {response.status_code}")
        return None

    except Exception as e:
        logger.error(f"❌ Không thể kết nối LPR Service tại {url}: {e}")
        return None
