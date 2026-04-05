# Smart Parking System — BE Core

Hệ thống điều vận trung tâm (Central Business Logic) cho giải pháp Bãi đỗ xe thông minh. BE Core đóng vai trò là "bộ não" điều phối tín hiệu giữa phần cứng (ESP32), AI nhận diện (BE LPR) và giao diện quản lý (Dashboard).

## 🏗 Kiến trúc Hệ thống
Dự án được xây dựng dựa trên kiến trúc **Event-Driven** (MQTT) kết hợp **REST API** (FastAPI):
- **MQTT**: Lắng nghe sensors (vào/ra/đỗ) và điều khiển thiết bị (Barrier).
- **FastAPI**: Cung cấp API trực tiếp cho Dashboard đọc dữ liệu từ Database.
- **SQLAlchemy**: Quản lý trực tiếp Database Supabase Postgres.
- **Service Layer**: Tách biệt logic kinh doanh (Tính tiền, Quản lý phiên đỗ xe).

## 📁 Cấu trúc Thư mục
```text
src/app/
├── api/             # Các Endpoint FastAPI (Sessions, Invoices, Slots)
├── core/            # Cấu hình trung tâm (Database, Config, CORS)
├── models/          # Định nghĩa Database Models (SQLAlchemy)
├── mqtt/            # Client MQTT và Router xử lý sự kiện
├── services/        # Logic nghiệp vụ (Gate, Payment, Slot, Pricing, LPR Client)
└── utils/           # Tiện ích chung (Logger)
main.py              # Entry point tập trung (Chạy đồng thời FastAPI + MQTT)
requirements.txt     # Danh sách thư viện ổn định (Paddle 2.6.x)
tests/               # Các script giả lập phần cứng và AI để testing
```

## 🛠 Cài đặt & Chạy bản Test
Xem hướng dẫn chi tiết tại [HUONG_DAN_CHAY.md](./HUONG_DAN_CHAY.md).

1. **Cài đặt thư viện**:
   ```powershell
   pip install -r requirements.txt
   ```

2. **Cấu hình môi trường**:
   Kiểm tra file `.env` đã có đúng `DATABASE_URL` của Supabase.

3. **Khởi chạy hệ thống**:
   ```powershell
   python main.py
   ```

## 📡 MQTT Topics
- **Sensors Input**: `ptithcm_2022/smart_parking/sensors` (Lắng nghe từ ESP32)
- **Control Output**: `ptithcm_2022/smart_parking/control` (Gửi lệnh mở Barrier/Thanh toán)

---
**Author**: Antigravity AI Assistant
**Status**: Refactored & Optimized (2026-04-05)
