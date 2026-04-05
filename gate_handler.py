import asyncio
import logging
import time
from mqtt_client import MQTTClient
from camera_service import capture_image_from_camera
from lpr_service import lpr_service
from parking_api_client import create_parking_session, update_parking_session

logger = logging.getLogger("gate_handler")


def handle_gate_event(gate: str, status: str, mqtt: MQTTClient, loop: asyncio.AbstractEventLoop):
    """
    Callback khi ESP32 báo có xe tại cổng.
    Hàm này chạy trong MQTT thread → dùng asyncio.run_coroutine_threadsafe
    để gọi async code từ thread khác.
    """
    logger.info(f"🚗 Bắt đầu xử lý sự kiện: {gate} - {status}")

    # 1. Chụp ảnh từ camera IP
    image_bytes = capture_image_from_camera()
    if image_bytes is None:
        logger.error("❌ Không chụp được ảnh → bỏ qua sự kiện")
        return

    # 2. Nhận diện biển số (async → phải schedule vào event loop chính)
    async def _recognize_and_process():
        plate_number = await lpr_service.recognize_plate(image_bytes)
        logger.info(f"🔍 Kết quả nhận diện: {plate_number}")

        if plate_number in ("Không nhận diện được", "Không tìm thấy nội dung biển số"):
            logger.warning("⚠️ Không nhận diện được biển số, bỏ qua")
            return

        # 3. Publish kết quả LPR lên MQTT
        mqtt.publish_lpr_result(gate, plate_number)

        # 4. Gọi API Dashboard thay vì truy cập DB trực tiếp
        result = _call_dashboard_api(plate_number, gate, image_bytes)

        if result is None:
            return

        # 5. Gửi lệnh mở cổng
        if gate == "GATE_IN":
            mqtt.publish_servo_open("GATE_IN")
        elif gate == "GATE_OUT":
            fee = result.get("fee", 0.0)
            if fee and float(fee) > 0:
                mqtt.publish_payment_request(
                    session=f"S{int(time.time())}",
                    invoice=f"INV{int(time.time())}",
                    cost=str(int(float(fee))),
                )
                logger.info("⏳ Chờ xác nhận thanh toán từ ESP32...")
            else:
                mqtt.publish_servo_open("GATE_OUT")

    # Schedule async function vào event loop
    future = asyncio.run_coroutine_threadsafe(_recognize_and_process(), loop)
    try:
        future.result(timeout=30)
    except Exception as e:
        logger.error(f"❌ Lỗi xử lý gate event: {e}")


def _call_dashboard_api(plate_number: str, gate: str, image_bytes: bytes) -> dict | None:
    """
    Gọi API parking-sessions của Dashboard dựa trên loại cổng.
    GATE_IN  → POST (tạo phiên mới)
    GATE_OUT → PUT  (cập nhật phiên - xe ra)
    """
    if gate == "GATE_IN":
        return create_parking_session(plate_number, image_bytes)
    elif gate == "GATE_OUT":
        return update_parking_session(plate_number, image_bytes)
    return None
