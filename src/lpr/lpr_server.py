import os
import random
import cv2
import numpy as np
import logging
import httpx
from fastapi import FastAPI
import uvicorn
from paddleocr import PaddleOCR

# Tắt lỗi hệ thống Paddle
os.environ['FLAGS_enable_pir_api'] = '0'
logging.getLogger('ppocr').setLevel(logging.ERROR)

app = FastAPI(title="LPR Service (Native Camera Capture)")

# === CẤU HÌNH CAMERA (Thay IP điện thoại của bạn vào đây) ===
CAMERA_URL = "http://192.168.1.10:8080/capture" # Ví dụ
IMAGE_DIR = r"E:\HocTap\AI\Doan\smart-parking-backend-core\tests\image"

# Khởi tạo OCR
try:
    ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False, use_gpu=False)
except:
    ocr = PaddleOCR(lang='en')

async def capture_from_phone():
    """Thực hiện lệnh GET /capture sang điện thoại để lấy ảnh binary"""
    try:
        print(f"📸 Đang gọi Camera: {CAMERA_URL}...")
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(CAMERA_URL)
            if response.status_code == 200:
                # Chuyển binary ảnh sang OpenCV format
                arr = np.frombuffer(response.content, np.uint8)
                img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
                return img, "camera_capture.jpg"
    except Exception as e:
        print(f"⚠️ Không kết nối được Camera ({e}). Chuyển sang ảnh Test Local.")
    return None, None

def get_random_local_img():
    """Lấy ảnh dự phòng khi camera offline"""
    images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not images: return None, None
    selected = random.choice(images)
    img = cv2.imread(os.path.join(IMAGE_DIR, selected))
    return img, selected

@app.post("/recognize")
async def recognize(data: dict):
    gate = data.get("gate", "unknown")
    
    # === [LUỒNG CỦA BẠN] ===
    # 1. Gọi GET /capture (Có fallback)
    img, img_name = await capture_from_phone()
    if img is None:
        img, img_name = get_random_local_img()

    if img is None:
        return {"plate": "ERROR_NO_IMAGE", "image_url": None}

    # 2. [Task A] AI nhận diện biển số
    result = ocr.ocr(img)
    
    detected_texts = []
    if result and result[0]:
        for line in result[0]:
            text = line[1][0]
            if line[1][1] > 0.5:
                clean_text = "".join(e for e in text if e.isalnum())
                detected_texts.append(clean_text)
    
    plate = "".join(detected_texts).upper()
    if not plate: plate = f"XE_{random.randint(100, 999)}"
    
    # 3. [Task B] Upload ảnh (Mock URL)
    # Ở đây sau này bạn sẽ viết code upload img lên Supabase Storage
    mock_url = f"https://supabase-mock.com/{img_name}"
    
    print(f"🔍 [LPR] Kết quả nhận diện: {plate}")
    
    return {
        "plate": plate,
        "image_url": mock_url
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
