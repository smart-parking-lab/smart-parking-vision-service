import asyncio
import logging
import time
from mqtt_client import MQTTClient
from camera_service import capture_image_from_camera
from lpr_service import lpr_service
from database import database, parking_logs
from datetime import datetime
import sqlalchemy

logger = logging.getLogger("gate_handler")


async def _process_parking_logic(plate_number: str, gate: str):
    """
    Xử lý logic vào/ra bãi dựa trên cổng (GATE_IN = vào, GATE_OUT = ra).
    """
    if plate_number in ("Không nhận diện được", "Không tìm thấy nội dung biển số"):
        return None

    now = datetime.utcnow()

    if gate == "GATE_IN":
        # Xe vào bãi - tạo record mới
        insert_query = parking_logs.insert().values(
            plate_number=plate_number,
            entry_time=now,
            status="in",
        )
        await database.execute(insert_query)
        logger.info(f"✅ Ghi nhận xe {plate_number} VÀO bãi")
        return {
            "action": "in",
            "plate_number": plate_number,
            "entry_time": now.isoformat(),
            "fee": 0.0,
        }

    elif gate == "GATE_OUT":
        # Xe ra bãi - tìm record đang "in"
        query = parking_logs.select().where(
            sqlalchemy.and_(
                parking_logs.c.plate_number == plate_number,
                parking_logs.c.status == "in",
            )
        )
        existing_record = await database.fetch_one(query)

        if existing_record:
            entry_time = existing_record["entry_time"]
            duration = now - entry_time
            duration_hours = duration.total_seconds() / 3600.0
            hours_rounded = max(1, round(duration_hours + 0.49))
            fee = hours_rounded * 10000.0

            update_query = (
                parking_logs.update()
                .where(parking_logs.c.id == existing_record["id"])
                .values(exit_time=now, status="out", fee=fee)
            )
            await database.execute(update_query)
            logger.info(f"✅ Ghi nhận xe {plate_number} RA bãi. Phí: {fee:,.0f} VND")
            return {
                "action": "out",
                "plate_number": plate_number,
                "entry_time": entry_time.isoformat(),
                "exit_time": now.isoformat(),
                "fee": fee,
            }
        else:
            logger.warning(f"⚠️ Xe {plate_number} không có trong bãi, không thể tính phí")
            return None

    return None


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

        # 4. Xử lý DB (vào/ra)
        result = await _process_parking_logic(plate_number, gate)

        if result is None:
            return

        # 5. Gửi lệnh mở cổng
        if result["action"] == "in":
            mqtt.publish_servo_open("GATE_IN")
        elif result["action"] == "out":
            # Nếu có phí → gửi yêu cầu thanh toán trước, rồi mới mở cổng sau
            fee = result.get("fee", 0.0)
            if fee > 0:
                mqtt.publish_payment_request(
                    session=f"S{int(time.time())}",
                    invoice=f"INV{int(time.time())}",
                    cost=str(int(fee)),
                )
                # Cổng sẽ được mở sau khi ESP32 xác nhận thanh toán thành công
                logger.info("⏳ Chờ xác nhận thanh toán từ ESP32...")
            else:
                mqtt.publish_servo_open("GATE_OUT")

    # Schedule async function vào event loop
    future = asyncio.run_coroutine_threadsafe(_recognize_and_process(), loop)
    try:
        future.result(timeout=30)
    except Exception as e:
        logger.error(f"❌ Lỗi xử lý gate event: {e}")
