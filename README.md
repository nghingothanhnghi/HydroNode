# HydroNode — ESP32 MicroPython Hydroponics Controller

HydroNode is an ESP32-based firmware for smart hydroponic automation, enabling real-time monitoring, sensor data collection, and automated control of pumps, lights, and other devices.

This folder contains the MicroPython source code for the ESP32 controller that manages sensors and actuators in the hydroponic system.

## Folder Structure

- **`main.py`**: Entry point of the application. Handles the main loop, network stability, and coordination between modules.
- **`config.py`**: Centralized configuration (WiFi credentials, backend URLs, GPIO mapping, and global runtime state).
- **`secrets.py`** *(gitignored, not included)*: Auth credentials (`AUTH_USERNAME`, `AUTH_PASSWORD`) imported by `config.py`.
- **`auth.py`**: Logs in to the backend at boot (and on 401) to obtain a fresh JWT, so the firmware never relies on a static token that can expire or be invalidated by a DB wipe.
- **`sensors.py`**: Logic for reading sensors — DHT11 (temp/humidity), analog EC/PPM, and the analog rain sensor.
- **`relay.py`**: Hardware abstraction for relays and the PWM/mosfet-driven water pump (active-low relay logic). Manages GPIO pins and the `MAX_ON_TIME` safety timeout.
- **`control.py`**: Logic for fetching commands from the backend and local auto-control (if `AUTO_MODE` is enabled), including a local rain-safety override.
- **`wifi.py`**: Manages WiFi connection, reconnection, and connectivity diagnostics (gateway/backend reachability tests).
- **`device.py` / `device_id.py`**: Device identification (derived from the ESP32's MAC address) and registration with the FastAPI backend.
- **`actuators.py`**: Registration of local actuators (Pump, Fan, Light, Water Pump, Valve) with the backend.
- **`oled_display.py` / `ssd1306.py`**: Driver and logic for the local I2C OLED status display.
- **`helper.py`**: Shared logging (`log`, `pretty`) and an HTTP request wrapper that enforces a socket timeout.

## System Flow

```mermaid
flowchart TD
    Boot["ESP32 Boot (main.py)"] --> WiFi["Connect WiFi (wifi.py)"]
    WiFi --> Auth["Login / Refresh JWT (auth.py)"]
    Auth --> Reg["Register Device & Actuators (device.py/actuators.py)"]

    subgraph Loop ["Main Loop (Infinite)"]
        Read["Read Sensors (sensors.py)"] --> Auto["Optional Local Auto-Control (control.py)"]
        Auto --> Send["POST /sensor/data (main.py)"]
        Send --> Fetch["GET /hydro/status (control.py)"]
        Fetch --> UpdateState["Update Local ACTUATOR_STATES"]
        UpdateState --> Apply["Apply GPIO States (relay.py)"]
        Apply --> Display["Update OLED (oled_display.py)"]
    end

    Reg --> Loop
```

## Data Integration

1. **Sensor Upload**: Every `SEND_INTERVAL` (default 10s), the ESP32 sends a JSON payload to the FastAPI `/sensor/data` endpoint, including temperature, humidity, EC/PPM, and rain (`rain_detected` / `rain_intensity`), each paired with a `*_valid` flag.
2. **Command Polling**: After sending data, the ESP32 calls `/hydro/status` to receive the latest desired state for its actuators (determined by backend rules or manual overrides).
3. **Safety**:
   - `relay.py` includes a `MAX_ON_TIME` safety feature to prevent actuators (like the pump) from running indefinitely if a "turn off" command is missed.
   - `control.py`'s local `auto_control()` forces the pump, water pump, and valve OFF whenever a valid rain reading is detected — a local fallback for the backend's `rain_detected_action` rule in case connectivity is lost.
   - Auth tokens are minted fresh at boot (`auth.py`) rather than baked into the firmware, so a backend DB wipe or 30-day token expiry doesn't require a reflash — only recreating the same username/password on the backend.

## Pin Mapping (Actual — matches `config.py` / `sensors.py`)

| Component | ESP32 Pin | Logic |
| :--- | :--- | :--- |
| **DHT11 (Temp/Hum)** | GPIO 14 | Digital |
| **EC Sensor** | GPIO 34 | Analog |
| **Rain Sensor** | GPIO 35 | Analog |
| **Pump Relay** | GPIO 25 | Active LOW |
| **Fan Relay** | GPIO 23 | Active LOW |
| **Light Relay** | GPIO 27 | Active LOW |
| **Water Pump** | GPIO 16 | PWM / Mosfet |
| **Valve Relay** | GPIO 18 | Active LOW |
| **OLED (SDA/SCL)** | GPIO 21 / 22 | I2C |

> ⚠️ GPIO pins are defined centrally in `config.TYPE_TO_GPIO` / `config.TYPE_TO_HARDWARE`. If you rewire a component, update `config.py` — this table should always match it.
