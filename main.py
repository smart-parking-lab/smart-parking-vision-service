import sys
import asyncio
import signal
from pathlib import Path

# Thêm src vào module path
src_path = Path(__file__).parent / "src"
sys.path.append(str(src_path))

import uvicorn
from app.main import app
from app.utils.logger import setup_logging, get_logger
from app.mqtt.client import MQTTClient
from app.mqtt.handlers import init_handlers, route_message
from app.core.config import SERVER_HOST, SERVER_PORT

logger = get_logger("be_core")

# Cờ duy trì vòng lặp
_keep_running = True


def _handle_exit(sig, frame):
    global _keep_running
    logger.info(f"🛑 Nhận tín hiệu thoát (signal {sig}). Đang dừng...")
    _keep_running = False


async def main():
    global _keep_running

    setup_logging()

    signal.signal(signal.SIGINT, _handle_exit)
    signal.signal(signal.SIGTERM, _handle_exit)

    loop = asyncio.get_running_loop()

    # === Khởi tạo MQTT ===
    mqtt_client = MQTTClient(on_message_callback=route_message)
    init_handlers(mqtt_client, loop)
    mqtt_client.connect()
    logger.info("✅ MQTT client đã khởi tạo")

    # === Khởi tạo FastAPI (chạy uvicorn trên thread riêng) ===
    config = uvicorn.Config(
        app,
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="info",
    )
    server = uvicorn.Server(config)

    # Chạy uvicorn trong task riêng
    server_task = asyncio.create_task(server.serve())

    logger.info("=" * 55)
    logger.info("🚀 BE Core — Smart Parking đang chạy!")
    logger.info(f"   📡 MQTT: Đang lắng nghe sensors từ ESP32")
    logger.info(f"   🌐 API:  http://{SERVER_HOST}:{SERVER_PORT}")
    logger.info(f"   📚 Docs: http://{SERVER_HOST}:{SERVER_PORT}/docs")
    logger.info("=" * 55)

    try:
        # Chờ cho đến khi có tín hiệu thoát
        while _keep_running:
            await asyncio.sleep(1)
    finally:
        # Cleanup
        server.should_exit = True
        await server_task
        mqtt_client.disconnect()
        logger.info("👋 BE Core đã thoát.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
