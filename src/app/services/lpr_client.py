import httpx
from app.core.config import LPR_SERVICE_URL
from app.utils.logger import get_logger

logger = get_logger("lpr_client")

REQUEST_TIMEOUT = 15.0


async def recognize_plate(gate: str) -> dict | None:
    """
    Gọi BE LPR: POST /recognize { gate: "entry" | "exit" }
    BE LPR sẽ tự chụp ảnh + AI nhận diện + upload ảnh.

    Returns:
        { "plate": "51A123", "image_url": "https://..." } hoặc None nếu lỗi.
    """
    url = f"{LPR_SERVICE_URL}/recognize"
    payload = {"gate": gate}

    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(url, json=payload)

        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ BE LPR trả: plate={result.get('plate')}")
            return result

        logger.error(f"❌ BE LPR trả HTTP {response.status_code}: {response.text}")
        return None

    except httpx.ConnectError:
        logger.error(f"❌ Không thể kết nối BE LPR tại {LPR_SERVICE_URL}")
        return None
    except httpx.TimeoutException:
        logger.error("❌ Timeout khi gọi BE LPR")
        return None
    except Exception as e:
        logger.error(f"❌ Lỗi gọi BE LPR: {e}")
        return None
