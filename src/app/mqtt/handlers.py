import asyncio
from app.utils.logger import get_logger
from app.core.database import get_db_session
from app.services.gate_service import handle_entry, handle_exit
from app.services.payment_service import handle_payment_confirmation
from app.services.slot_service import handle_slot_update

logger = get_logger("mqtt_handlers")

# Reference tới MQTT client, được set khi khởi tạo
_mqtt_client = None
_event_loop = None


def init_handlers(mqtt_client, loop: asyncio.AbstractEventLoop):
    """Khởi tạo reference global cho handlers."""
    global _mqtt_client, _event_loop
    _mqtt_client = mqtt_client
    _event_loop = loop


def route_message(topic: str, data: dict):
    """
    Phân luồng MQTT message tới service tương ứng.
    Hàm này chạy trong MQTT thread → dùng run_coroutine_threadsafe.
    """
    sensor = data.get("sensor", "")
    target = data.get("target", "")
    status = data.get("status", "")

    # === Cổng vào/ra: chỉ xử lý khi có xe ===
    if sensor in ("GATE_IN", "GATE_OUT") and status == "CO_XE":
        logger.info(f"🚨 Phát hiện xe tại {sensor}")
        _dispatch_async(_handle_gate_event(sensor))
        return

    # === Slot cảm biến ===
    if sensor in ("SLOT_1", "SLOT_2", "SLOT_3", "SLOT_4"):
        logger.info(f"🅿️ Slot {sensor}: {status}")
        _dispatch_async(_handle_slot_event(sensor, status))
        return

    # === Thanh toán từ ESP32 ===
    if target == "PAYMENT" and status == "paid":
        invoice_id = data.get("invoice", "")
        session_id = data.get("session", "")
        logger.info(f"💳 Nhận xác nhận thanh toán: invoice={invoice_id}")
        _dispatch_async(_handle_payment_event(invoice_id, session_id))
        return

    # === Heartbeat ===
    if target == "HEARTBEAT" or sensor == "HEARTBEAT":
        logger.info("💓 Nhận heartbeat từ ESP32")
        return

    logger.debug(f"⏭️ Message không cần xử lý: {data}")


def _dispatch_async(coro):
    """Schedule async coroutine vào event loop chính."""
    if _event_loop is None:
        logger.error("❌ Event loop chưa được khởi tạo")
        return

    future = asyncio.run_coroutine_threadsafe(coro, _event_loop)
    try:
        future.result(timeout=30)
    except Exception as e:
        logger.error(f"❌ Lỗi xử lý MQTT event: {e}")


async def _handle_gate_event(gate: str):
    """Xử lý sự kiện cổng vào/ra."""
    db = get_db_session()
    try:
        if gate == "GATE_IN":
            await handle_entry(db, _mqtt_client)
        elif gate == "GATE_OUT":
            await handle_exit(db, _mqtt_client)
    finally:
        db.close()


async def _handle_slot_event(sensor: str, status: str):
    """Xử lý cập nhật trạng thái slot."""
    db = get_db_session()
    try:
        handle_slot_update(db, sensor, status)
    finally:
        db.close()


async def _handle_payment_event(invoice_id: str, session_id: str):
    """Xử lý xác nhận thanh toán từ ESP32."""
    db = get_db_session()
    try:
        handle_payment_confirmation(db, invoice_id, session_id, _mqtt_client)
    finally:
        db.close()
