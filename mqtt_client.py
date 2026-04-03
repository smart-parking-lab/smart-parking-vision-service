import paho.mqtt.client as mqtt
import json
import time
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("mqtt_client")

# Cấu hình MQTT từ .env
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "be1_lpr")

# Topic phải khớp 100% với ESP32 (arduino_hardware.ino)
TOPIC_SENSOR = "ptithcm_2022/smart_parking/sensors"
TOPIC_CONTROL = "ptithcm_2022/smart_parking/control"


class MQTTClient:
    """MQTT Client cho BE1 (LPR Service) - lắng nghe sensor và gửi lệnh điều khiển."""

    def __init__(self, on_gate_event=None):
        """
        Args:
            on_gate_event: Callback khi phát hiện xe tại cổng.
                           Signature: on_gate_event(gate: str, status: str)
                           gate = "GATE_IN" | "GATE_OUT"
                           status = "CO_XE" | "TRONG"
        """
        self._on_gate_event = on_gate_event
        self._client = mqtt.Client(client_id=MQTT_CLIENT_ID)
        self._client.on_connect = self._handle_connect
        self._client.on_message = self._handle_message
        self._client.on_disconnect = self._handle_disconnect
        self._is_connected = False

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    def _handle_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"✅ MQTT đã kết nối broker ({MQTT_BROKER}:{MQTT_PORT})")
            # Subscribe topic sensor để nhận tín hiệu từ ESP32
            client.subscribe(TOPIC_SENSOR, qos=1)
            logger.info(f"🎧 Đang lắng nghe topic: {TOPIC_SENSOR}")
            self._is_connected = True
        else:
            logger.error(f"❌ MQTT kết nối thất bại, mã lỗi: {rc}")

    def _handle_disconnect(self, client, userdata, rc):
        self._is_connected = False
        if rc != 0:
            logger.warning(f"⚠️ MQTT mất kết nối bất ngờ (rc={rc}), đang thử kết nối lại...")

    def _handle_message(self, client, userdata, msg):
        """Xử lý message từ ESP32 trên topic sensor."""
        try:
            payload = msg.payload.decode("utf-8")
            logger.info(f"📩 MQTT nhận: topic={msg.topic} | payload={payload}")

            data = json.loads(payload)
            sensor = data.get("sensor", "")
            status = data.get("status", "")
            target = data.get("target", "")

            # Chỉ xử lý sự kiện GATE (cổng vào/ra) khi có xe
            if sensor in ("GATE_IN", "GATE_OUT") and status == "CO_XE":
                logger.info(f"🚨 Phát hiện xe tại {sensor}!")
                if self._on_gate_event:
                    self._on_gate_event(sensor, status)

            elif sensor in ("SLOT_1", "SLOT_2"):
                logger.info(f"🅿️ Slot {sensor}: {status}")

            elif target == "PAYMENT":
                # ESP32 trả kết quả thanh toán
                payment_status = data.get("status", "")
                logger.info(f"💳 Kết quả thanh toán: {payment_status}")

        except json.JSONDecodeError:
            logger.error("⚠️ Message không phải JSON hợp lệ")
        except Exception as e:
            logger.error(f"❌ Lỗi xử lý MQTT message: {e}")

    def connect(self):
        """Kết nối tới MQTT broker và bắt đầu vòng lặp nền."""
        try:
            self._client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            # loop_start() chạy vòng lặp MQTT trên thread riêng (non-blocking)
            self._client.loop_start()
            logger.info("🔄 MQTT loop đã khởi động (background thread)")
        except Exception as e:
            logger.error(f"❌ Không thể kết nối MQTT: {e}")

    def disconnect(self):
        """Ngắt kết nối MQTT."""
        self._client.loop_stop()
        self._client.disconnect()
        self._is_connected = False
        logger.info("🔌 Đã ngắt kết nối MQTT")

    def publish_servo_open(self, gate: str):
        """
        Gửi lệnh mở cổng tới ESP32.
        Args:
            gate: "GATE_IN" hoặc "GATE_OUT"
        """
        servo_target = "SERVO_IN" if gate == "GATE_IN" else "SERVO_OUT"
        payload = json.dumps({"target": servo_target, "command": "OPEN"})
        self._client.publish(TOPIC_CONTROL, payload, qos=1)
        logger.info(f"📤 Đã gửi lệnh mở cổng: {servo_target}")

    def publish_payment_request(self, session: str, invoice: str, cost: str):
        """
        Gửi yêu cầu thanh toán tới ESP32.
        """
        payload = json.dumps({
            "target": "PAYMENT",
            "status": "START",
            "session": session,
            "invoice": invoice,
            "cost": cost,
        })
        self._client.publish(TOPIC_CONTROL, payload, qos=1)
        logger.info(f"📤 Đã gửi yêu cầu thanh toán: session={session}, cost={cost}")

    def publish_lpr_result(self, gate: str, plate_number: str):
        """
        Publish kết quả nhận diện biển số lên topic sensor
        để BE2 hoặc hệ thống khác có thể lấy.
        """
        payload = json.dumps({
            "source": "LPR",
            "gate": gate,
            "plate": plate_number,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        })
        self._client.publish(TOPIC_SENSOR, payload, qos=1)
        logger.info(f"📤 Đã publish kết quả LPR: {plate_number} tại {gate}")
