# config.py
# ================================
# 🔐 DEVICE ID (unique per ESP32)
# ================================
from device_id import get_device_code

DEVICE_CODE = get_device_code()
# 👉 This is sent to backend as `device_id`
# 👉 Backend stores it in HydroDevice.device_id (STRING, unique)

# ================================
# 📶 WIFI CONFIG
# ================================
SSID = "Oanh Nguyen 2.4Ghz"
PASSWORD = "71237123"

# ================================
# 🌐 BACKEND BASE URL
# ================================
FASTAPI_URL = "http://192.168.1.41:8000"

# ================================
# 👤 AUTH / USER CONTEXT
# ================================
CLIENT_ID = "706cfcdc-5e1c-4bae-b159-f66425c81ecc"
USER_ID = 1

AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc4MzIzMTk3N30.kKrz17Yv4APknT1Sb5pOu3dzDpUj1glhmQNa6i9Mu7w"

HEADERS = {
    "Authorization": "Bearer " + AUTH_TOKEN,
    "Content-Type": "application/json"
}

# ================================
# 🔗 API ROUTES (MATCH BACKEND)
# ================================

# Device (ESP32 registration)
DEVICE_URL = FASTAPI_URL + "/hydro/devices"
# ↔ POST → create device
# ↔ GET  → list devices

# Sensor data
SENSOR_URL = FASTAPI_URL + "/sensor/data"
# ↔ POST → send sensor data

# Actuators
ACTUATOR_URL = FASTAPI_URL + "/actuators"
ACTUATOR_BULK_URL = ACTUATOR_URL + "/bulk"
# ↔ POST bulk → register actuators

# System status (IMPORTANT)
STATUS_URL = FASTAPI_URL + "/hydro/status"
# ↔ GET → ESP32 fetch commands from backend

# ================================
# 🤖 AUTO MODE FLAG
# ================================
AUTO_MODE = {"enabled": False}   # mutable dictionary
# 👉 If True → ESP32 uses local logic (auto_control)
# 👉 If False → controlled by backend

# ================================
# ⚡ GPIO MAPPING (CRITICAL)
# ================================
# Map actuator type → GPIO PIN (STRING)

TYPE_TO_GPIO = {
    "pump": "25",
    "fan": "23",
    "light": "27",
    "water_pump": "16",
    "valve": "18",
}

TYPE_TO_HARDWARE = {
    "pump": "relay",
    "fan": "relay",
    "light": "relay",
    "water_pump": "mosfet",   # 👈 THIS is enough
    "valve": "relay",
}

# 0–100 (%)
PUMP_SPEED = {
    "16": 0
}

# ================================
# 🔌 RUNTIME STATE STORAGE
# ================================
# This is what actually drives relays

ACTUATOR_STATES = {
    "25": 0,
    "23": 0,
    "27": 0,
    "16": 0,
    "18": 0,
}

# Backend logic:
# 1 = actuator ON
# 0 = actuator OFF

# Relay hardware is ACTIVE LOW:
# GPIO LOW  -> relay ON
# GPIO HIGH -> relay OFF


# ================================
# ⏱ TIMING CONFIG
# ================================
SEND_INTERVAL = 10  # seconds (send sensor data)
RETRY_DELAY = 5     # seconds (retry when failed)

