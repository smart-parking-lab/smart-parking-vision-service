import paho.mqtt.client as mqtt
import json
import time

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "ptithcm_2022/smart_parking/sensors"

client = mqtt.Client()
client.connect(BROKER, PORT)
client.loop_start()

def trigger_gate_entry():
    payload = {"sensor": "GATE_IN", "status": "CO_XE"}
    client.publish(TOPIC, json.dumps(payload))
    print("\n🚗 [Mock HW] ---> Gửi: CÓ XE TẠI CỔNG VÀO (GATE_IN)")

def trigger_gate_exit():
    payload = {"sensor": "GATE_OUT", "status": "CO_XE"}
    client.publish(TOPIC, json.dumps(payload))
    print("\n🚗 [Mock HW] ---> Gửi: CÓ XE TẠI CỔNG RA (GATE_OUT)")

def trigger_slot(slot_id, is_occupied):
    status = "CO_XE" if is_occupied else "TRONG"
    payload = {"sensor": f"SLOT_{slot_id}", "status": status}
    client.publish(TOPIC, json.dumps(payload))
    print(f"🅿️ [Mock HW] ---> Gửi: Cập nhật SLOT_{slot_id} = {status}")

def trigger_payment_confirm():
    """Giả lập ESP32 xác nhận đã thanh toán."""
    invoice_id = input("Nhập invoice_id (xem ở log BE Core): ")
    session_id = input("Nhập session_id (xem ở log BE Core): ")
    
    payload = {
        "target": "PAYMENT",
        "status": "paid",
        "invoice": invoice_id,
        "session": session_id
    }
    client.publish(TOPIC, json.dumps(payload))
    print(f"💳 [Mock HW] ---> Gửi: XÁC NHẬN THANH TOÁN (Invoice: {invoice_id})")

if __name__ == "__main__":
    print("\n--- TRÌNH GIẢ LẬP PHẦN CỨNG (CẬP NHẬT) ---")
    print("1. Xe VÀO")
    print("2. Xe RA (Sẽ tạo Invoice)")
    print("3. Xe ĐỖ VÀO SLOT 1")
    print("4. Xe RỜI KHỎI SLOT 1")
    print("5. XÁC NHẬN THANH TOÁN (Mở barrier ra)")
    print("0. Thoát")
    
    try:
        while True:
            choice = input("\nChọn lệnh (0-5): ")
            if choice == "1": trigger_gate_entry()
            elif choice == "2": trigger_gate_exit()
            elif choice == "3": trigger_slot(1, True)
            elif choice == "4": trigger_slot(1, False)
            elif choice == "5": trigger_payment_confirm()
            elif choice == "0": break
            time.sleep(1)
    except KeyboardInterrupt: pass
    finally:
        client.loop_stop()
        client.disconnect()
