# 🚀 Hướng Dẫn Chạy BE Core

Mở 3 Terminal song song theo thứ tự sau:

### 1. Terminal 1: BE Core (Port 8000)
```powershell
.\venv\Scripts\activate
python main.py
```

### 2. Terminal 2: Mock LPR (Port 8001)
```powershell
.\venv\Scripts\activate
python tests/mock_lpr.py
```

### 3. Terminal 3: Mock Hardware (MQTT Test)
```powershell
.\venv\Scripts\activate
python tests/mock_hw.py
```

---
## 🛠 Quy trình Test hoàn chỉnh:
1. **Xe vào**: Terminal 3 bấm **1**. Kiểm tra log Terminal 1 & 2.
2. **Xe đỗ**: Terminal 3 bấm **3**. Kiểm tra Slot tại `http://localhost:8000/api/v1/parking-slots`.
3. **Xe ra**: Terminal 3 bấm **2**. Xem `invoice_id` ở log Terminal 1.
4. **Thanh toán**: Terminal 3 bấm **5**, dán `invoice_id` và `session_id` để mở Barrier.

**API Docs**: http://localhost:8000/docs
