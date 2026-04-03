# HƯỚNG DẪN CHẠY

## BƯỚC 1: Cài đặt (Chỉ làm 1 lần)
Mở Terminal tại thư mục `parking-lpr`:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## BƯỚC 2: Cấu hình hệ thống
Kiểm tra và sửa thông tin trong file `.env`:
- `IP_CAMERA`: Đặt IP của App điện thoại. Nếu không có đt, giữ nguyên (hệ thống tự lấy ảnh mẫu để test).
- `DATABASE_URL`: Cấu hình Postgres (Supabase).
- `MQTT_CLIENT_ID`: Độc nhất (Không trùng chéo với ai).

## BƯỚC 3: Chạy Worker CHÍNH
```bash
python main.py
```
*(Tiến trình sẽ treo liên tục ở nền để đợi lệnh. Nhấn Ctrl+C để tắt).*

---

## BƯỚC TEST (Khi không có trạm quét xe thật)
Mở Terminal mới (#2) và giả vờ làm xe đi qua cổng:
```bash
.\venv\Scripts\activate
python mock_esp32.py
```
-> Theo dõi Terminal 1 xem DB được lưu và Barrier được mở ra sao.
