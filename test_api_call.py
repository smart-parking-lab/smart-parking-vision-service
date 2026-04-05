"""
Script test luồng: Core LPR → nhận diện biển số → gọi API Dashboard.

Yêu cầu: Dashboard phải đang chạy tại DASHBOARD_API_URL (mặc định http://127.0.0.1:9000).

Cách dùng:
    python test_api_call.py
"""

import os
import sys
import logging
import asyncio

# Cấu hình env trước khi import các module khác
os.environ['FLAGS_use_mkldnn'] = '0'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from dotenv import load_dotenv
load_dotenv()

from lpr_service import lpr_service
from parking_api_client import create_parking_session, update_parking_session

# ========== Logger ==========
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)
logger = logging.getLogger("test")
logger.setLevel(logging.INFO)
# Also add a stream handler specifically for this logger if root is suppressed
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s", datefmt="%H:%M:%S")
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.propagate = False

# Thư mục chứa ảnh test
TEST_IMAGES_DIR = "test-images"


async def test_full_flow(image_filename: str):
    """Test toàn bộ luồng: đọc ảnh → nhận diện biển số → gọi API dashboard."""
    image_path = os.path.join(TEST_IMAGES_DIR, image_filename)

    if not os.path.exists(image_path):
        logger.error(f"❌ Không tìm thấy ảnh: {image_path}")
        return

    # 1. Đọc ảnh
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    logger.info(f"📸 Đã đọc ảnh {image_filename} ({len(image_bytes)} bytes)")

    # 2. Nhận diện biển số
    logger.info("🔍 Đang nhận diện biển số...")
    plate_number = await lpr_service.recognize_plate(image_bytes)
    logger.info(f"🔍 Kết quả nhận diện: {plate_number}")

    if plate_number in ("Không nhận diện được", "Không tìm thấy nội dung biển số"):
        logger.warning("⚠️ Không nhận diện được biển số, dừng test")
        return

    # 3. Gọi API Dashboard - Tạo phiên (xe vào)
    logger.info(f"📤 Gọi POST /parking-sessions (xe VÀO) với biển số: {plate_number}")
    result_in = create_parking_session(plate_number, image_bytes)

    if result_in:
        logger.info(f"✅ Tạo phiên thành công: {result_in}")
    else:
        logger.error("❌ Tạo phiên thất bại")
        return

    # 4. Gọi API Dashboard - Cập nhật phiên (xe ra)
    logger.info(f"📤 Gọi PUT /parking-sessions (xe RA) với biển số: {plate_number}")
    result_out = update_parking_session(plate_number, image_bytes)

    if result_out is not None:
        logger.info(f"✅ Cập nhật phiên thành công: {result_out}")
    else:
        logger.error("❌ Cập nhật phiên thất bại")


async def main():
    print("=" * 60)
    print("🧪 TEST: Core LPR → Dashboard API")
    print(f"📡 Dashboard URL: {os.getenv('DASHBOARD_API_URL', 'http://127.0.0.1:9000')}")
    print("=" * 60)

    # Lấy danh sách ảnh test
    if not os.path.isdir(TEST_IMAGES_DIR):
        logger.error(f"❌ Không tìm thấy thư mục {TEST_IMAGES_DIR}")
        return

    test_images = sorted(os.listdir(TEST_IMAGES_DIR))
    logger.info(f"📂 Tìm thấy {len(test_images)} ảnh test: {test_images}")

    # Chỉ test với ảnh đầu tiên
    test_image = test_images[0]
    logger.info(f"\n{'─' * 40}")
    logger.info(f"🖼️  Test với ảnh: {test_image}")
    logger.info(f"{'─' * 40}")
    await test_full_flow(test_image)


if __name__ == "__main__":
    asyncio.run(main())
