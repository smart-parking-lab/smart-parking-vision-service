# 🚀 Hướng Dẫn Chạy Smart Parking (2 Terminal Mode)

Hệ thống đã được thiết kế lại theo ý bạn: **Gọn nhẹ nhưng vẫn chuẩn kiến trúc**.

### 1. Terminal 1: Backend Hub (Core + LPR + AI)
```powershell
.\venv\Scripts\activate
python main.py
```
*   **Hệ thống sẽ tự khởi chạy song song:**
    *   **Core API (8000)**: Xử lý Business Logic, MQTT, Dashboard.
    *   **LPR API (8001)**: Xử lý AI, gọi `GET /capture` sang camera/điện thoại.
*   *Lưu ý:* Nếu camera điện thoại offline, LPR sẽ tự động lấy ảnh trong `tests/image` làm mẫu.

### 2. Terminal 2: Test Interface (Mock HW)
```powershell
.\venv\Scripts\activate
python tests/mock_hw.py
```

---
## 🛠 Các lệnh Test (Trong Terminal 2):
*   **Bấm 1**: Xe VÀO. (Core gọi LPR chụp ảnh -> AI đọc biển số -> Lưu DB).
*   **Bấm 2**: Xe RA. (Core gọi LPR -> Tính tiền dựa trên phí đã cấu hình).
*   **Bấm 3/4**: Giả lập tình trạng Slot 1 (Đầu cảm biến IR của ESP32).
*   **Bấm 5**: Xác nhận thanh toán xong (Để mở barrier cổng ra).

## 📡 Tài liệu API:
- **Swagger UI**: http://localhost:8000/docs
