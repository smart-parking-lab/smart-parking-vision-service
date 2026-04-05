import asyncio
import logging
import sys
import signal
from mqtt_client import MQTTClient
from gate_handler import handle_gate_event

# ========== Cấu hình Logger ==========
logger = logging.getLogger("worker_main")
logger.setLevel(logging.INFO)
if logger.hasHandlers():
    logger.handlers.clear()
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s", "%Y-%m-%d %H:%M:%S"))
logger.addHandler(handler)
logger.propagate = False

# Thiết lập level cho các module con
for module_name in ("mqtt_client", "camera_service", "gate_handler", "parking_api_client"):
    sub_logger = logging.getLogger(module_name)
    sub_logger.setLevel(logging.INFO)
    if not sub_logger.handlers:
        sub_logger.addHandler(handler)
    sub_logger.propagate = False

# Cờ để duy trì tiến trình chạy nền
keep_running = True

def handle_exit(sig, frame):
    global keep_running
    logger.info(f"🛑 Nhận tín hiệu ngắt vòng lặp (signal {sig}). Đang dừng graceful...")
    keep_running = False

async def main():
    global keep_running
    
    # Catch SIGINT (Ctrl+C) and SIGTERM
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # Lấy event loop
    loop = asyncio.get_running_loop()

    # Khởi tạo và kết nối MQTT
    mqtt_client = None
    try:
        def on_gate(gate: str, status: str):
            handle_gate_event(gate, status, mqtt_client, loop)

        mqtt_client = MQTTClient(on_gate_event=on_gate)
        mqtt_client.connect()
        logger.info("✅ MQTT client worker đã khởi tạo")
        
        # Vòng lặp duy trì tiến trình sống
        logger.info("🚀 LPR MQTT Worker đang chạy. Nhấn Ctrl+C để thoát.")
        while keep_running:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"❌ Lỗi runtime trong main loop: {e}")
    finally:
        # --- Cleanup ---
        if mqtt_client:
            mqtt_client.disconnect()
            logger.info("🔌 Đã ngắt kết nối MQTT")
            
        logger.info("👋 Worker đã thoát.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
