import os
import random
import cv2
import numpy as np
import logging

# Tắt lỗi hệ thống Paddle 3.x nếu có
os.environ['FLAGS_enable_pir_api'] = '0'

from fastapi import FastAPI
import uvicorn
from paddleocr import PaddleOCR

logging.getLogger('ppocr').setLevel(logging.ERROR)
app = FastAPI()

# Khởi tạo bản ổn định nhất
try:
    # Thử cấu hình bản 2.x/3.x cơ bản
    ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False, use_gpu=False)
except:
    ocr = PaddleOCR(lang='en')

IMAGE_DIR = r"E:\HocTap\AI\Doan\smart-parking-backend-core\tests\image"

def recognize_plate(image_path: str) -> str:
    try:
        img = cv2.imread(image_path)
        if img is None: return "Lỗi: File ảnh"

        # Tự động detect structure của PaddleOCR results
        result = ocr.ocr(img, cls=True) 
        
        if not result or not result[0]:
            return "Không thấy chữ"

        detected_texts = []
        for line in result[0]:
            text = line[1][0]
            confidence = line[1][1]
            if confidence > 0.5:
                clean_text = "".join(e for e in text if e.isalnum())
                detected_texts.append(clean_text)

        return "".join(detected_texts).upper() if detected_texts else "KHONG_DOC_DUOC"

    except Exception as e:
        # Nếu AI lỗi (do phiên bản), trả về biển TEST để còn test DB
        print(f"DEBUG AI: {e}")
        return f"XE_{random.randint(10,99)}"

@app.post("/recognize")
async def recognize(data: dict):
    gate = data.get("gate", "unknown")
    images = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    selected_image = random.choice(images) if images else "none.jpg"
    image_path = os.path.join(IMAGE_DIR, selected_image)
    
    print(f"\n📸 [Mock LPR] Đang xử lý: {selected_image}...")
    plate_result = recognize_plate(image_path)
    print(f"🔍 [Mock LPR] Kết quả: {plate_result}")
    
    return {"plate": plate_result, "image_url": "https://supabase.com/" + selected_image}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
