import json
import paho.mqtt.client as mqtt
from app.core.config import MQTT_BROKER, MQTT_PORT, MQTT_CLIENT_ID
from app.mqtt.topics import TOPIC_SENSOR, TOPIC_CONTROL
from app.utils.logger import get_logger

logger = get_logger("mqtt_client")


class MQTTClient:
    """MQTT Client cho BE Core — subscribe sensor, publish control."""

    def __init__(self, on_message_callback=None):
        """
        Args:
            on_message_callback: Hàm xử lý message thô.
                Signature: callback(topic: str, payload: dict)
        """
        self._on_message_callback = on_message_callback
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
            client.subscribe(TOPIC_SENSOR, qos=1)
            logger.info(f"🎧 Đang lắng nghe topic: {TOPIC_SENSOR}")
            self._is_connected = True
        else:
            logger.error(f"❌ MQTT kết nối thất bại, mã lỗi: {rc}")

    def _handle_disconnect(self, client, userdata, rc):
        self._is_connected = False
        if rc != 0:
            logger.warning(f"⚠️ MQTT mất kết nối bất ngờ (rc={rc})")

    def _handle_message(self, client, userdata, msg):
        """Parse JSON rồi chuyển cho callback xử lý."""
        try:
            payload_str = msg.payload.decode("utf-8")
            logger.info(f"📩 MQTT nhận: topic={msg.topic} | payload={payload_str}")
            data = json.loads(payload_str)

            if self._on_message_callback:
                self._on_message_callback(msg.topic, data)

        except json.JSONDecodeError:
            logger.error("⚠️ Message không phải JSON hợp lệ")
        except Exception as e:
            logger.error(f"❌ Lỗi xử lý MQTT message: {e}")

    def connect(self):
        """Kết nối tới MQTT broker và bắt đầu vòng lặp nền."""
        try:
            self._client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
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

    def publish(self, topic: str, payload: dict):
        """Publish JSON payload lên topic."""
        message = json.dumps(payload)
        self._client.publish(topic, message, qos=1)
        logger.info(f"📤 MQTT publish: topic={topic} | payload={message}")

    def publish_gate_open(self, gate: str):
        """Gửi lệnh mở barrier."""
        servo_target = "SERVO_IN" if gate == "GATE_IN" else "SERVO_OUT"
        self.publish(TOPIC_CONTROL, {"target": servo_target, "command": "OPEN"})

    def publish_payment_request(self, session_id: str, invoice_id: str, fee: str):
        """Gửi yêu cầu thanh toán tới ESP32."""
        self.publish(TOPIC_CONTROL, {
            "target": "PAYMENT",
            "status": "START",
            "session": session_id,
            "invoice": invoice_id,
            "cost": fee,
        })
