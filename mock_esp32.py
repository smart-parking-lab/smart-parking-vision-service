import paho.mqtt.client as mqtt
import json
import time

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_SENSOR = "ptithcm_2022/smart_parking/sensors"
TOPIC_CONTROL = "ptithcm_2022/smart_parking/control"

def on_connect(client, userdata, flags, rc):
    print("✅ [Tu ESP32 Gia lap] Da ket noi den MQTT Broker!")
    client.subscribe(TOPIC_CONTROL)
    print(f"🎧 [Tu ESP32 Gia lap] Dang lang nghe lenh tai {TOPIC_CONTROL}")
    
    # Giả lập phát hiện chiếc xe đầu tiên đi vào
    print("\n🚗 [Tu ESP32 Gia lap] -> Phat hien co xe tai GATE_IN! Gui tin hieu di...")
    payload = json.dumps({"sensor": "GATE_IN", "status": "CO_XE"})
    client.publish(TOPIC_SENSOR, payload)

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"\n📩 [Tu ESP32 Gia lap] Nhan duoc tin nhan tra ve: {payload}")
    
    try:
        data = json.loads(payload)
        if data.get("target") == "SERVO_IN" and data.get("command") == "OPEN":
            print("🔓 [Tu ESP32 Gia lap] Mo barrier cong vao thanh cong! Luong vao chuan xac.")
            # Chờ tí rồi tắt test
            time.sleep(1)
            client.disconnect()
    except Exception as e:
        pass

client = mqtt.Client(client_id="esp32_mock_v1")
client.on_connect = on_connect
client.on_message = on_message

print("Khởi động phần cứng giả lập...")
client.connect(BROKER, PORT, 60)
client.loop_forever()
