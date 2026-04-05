import sys
import asyncio
import signal
import threading
from pathlib import Path

# Thêm src vào module path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

import uvicorn
from app.main import app as core_app
from lpr.lpr_server import app as lpr_app
from app.utils.logger import setup_logging, get_logger
from app.mqtt.client import MQTTClient
from app.mqtt.handlers import init_handlers, route_message
from app.core.config import SERVER_HOST, SERVER_PORT

logger = get_logger("be_system")

# Cờ duy trì vòng lặp
_keep_running = True


def _handle_exit(sig, frame):
    global _keep_running
    logger.info(f"🛑 Nhận tín hiệu thoát. Đang dừng...")
    _keep_running = False


def run_lpr_service():
    """Hàm chạy LPR Service ở một thread riêng (Cổng 8001)"""
    logger.info("📡 Đang khởi động LPR Service tại cổng 8001...")
    uvicorn.run(lpr_app, host="127.0.0.1", port=8001, log_level="error")


async def main():
    global _keep_running

    setup_logging()
    signal.signal(signal.SIGINT, _handle_exit)
    signal.signal(signal.SIGTERM, _handle_exit)

    loop = asyncio.get_running_loop()

    # === 1. Khởi động LPR SERVICE (Thread riêng) ===
    lpr_thread = threading.Thread(target=run_lpr_service, daemon=True)
    lpr_thread.start()

    # === 2. Khởi tạo MQTT ===
    mqtt_client = MQTTClient(on_message_callback=route_message)
    init_handlers(mqtt_client, loop)
    mqtt_client.connect()
    logger.info("✅ MQTT client đã khởi tạo")

    # === 3. Khởi tạo BE CORE (FastAPI chính) ===
    config = uvicorn.Config(
        core_app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())

    logger.info("=" * 55)
    print("🚀 HỆ THỐNG SMART PARKING ĐÃ SẴN SÀNG (2 TERMINALS MODE)")
    print(f"   🌐 BE CORE: http://127.0.0.1:8000")
    print(f"   📷 BE LPR:  http://127.0.0.1:8001")
    logger.info("=" * 55)

    try:
        while _keep_running:
            await asyncio.sleep(1)
    finally:
        server.should_exit = True
        await server_task
        mqtt_client.disconnect()
        logger.info("👋 Toàn bộ hệ thống đã thoát.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
