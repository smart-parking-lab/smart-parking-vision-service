import os
from dotenv import load_dotenv

load_dotenv()


# ===== MQTT =====
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "be_core_smart_parking")

# ===== Database (Supabase PostgreSQL) =====
DATABASE_URL = os.getenv("DATABASE_URL", "")

# ===== Supabase Storage =====
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# ===== BE LPR =====
LPR_SERVICE_URL = os.getenv("LPR_SERVICE_URL", "http://127.0.0.1:8001")

# ===== Server =====
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
