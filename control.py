# control.py
import urequests as requests
import config
from helper import log, http_request
from device import shutdown_device, activate_device as activate_device_hardware

def auto_control(data):
    """
    Local auto-control. Only acts on a reading if its matching "_valid"
    flag is True — fallback/stub values (see sensors.py) must never
    drive a relay decision, since they're placeholders, not measurements.
    """
    def set_state(actuator_type, condition):
        gpio = config.TYPE_TO_GPIO.get(actuator_type)
        # ❌ DO NOT override if backend already ON
        if gpio and config.ACTUATOR_STATES.get(gpio) == 0:
            config.ACTUATOR_STATES[gpio] = 1 if condition else 0

    # 🌧 RAIN OVERRIDE — highest priority local safety check.
    # If rain is confirmed (valid reading) and detected, force water-related
    # actuators OFF regardless of moisture/other conditions, and skip the
    # rest of auto-control this cycle. This mirrors the backend's
    # rain_detected_action="close_door" rule as a local fallback in case
    # connectivity to the backend is lost.
    if data.get("rain_valid", False) and data.get("rain_detected", False):
        log("\U0001F327 Rain detected -> forcing pump/water actuators OFF", "yellow")
        for actuator_type in ("pump", "water_pump", "valve"):
            gpio = config.TYPE_TO_GPIO.get(actuator_type)
            if gpio:
                config.ACTUATOR_STATES[gpio] = 0
                if gpio in config.PUMP_SPEED:
                    config.PUMP_SPEED[gpio] = 0
        return

    if data["temperature_valid"] is not None:
        set_state("fan", data["temperature"] > 28)
    else:
        log("\u26A0 Skipping fan auto-control: temperature invalid", "yellow")

    if data["moisture_valid"] is not None:
        set_state("pump", data["moisture"] < 40)
    else:
        log("\u26A0 Skipping pump auto-control: moisture invalid", "yellow")

    if data["light_valid"] is not None:
        set_state("light", data["light"] < 300)
    else:
        log("\u26A0 Skipping light auto-control: light invalid", "yellow")

    if data["water_level_valid"] is not None:
        set_state("water_pump", data["water_level"] < 10)
    else:
        log("\u26A0 Skipping water_pump auto-control: water_level invalid", "yellow")        

def check_commands(device_id):
    res = None  # ✅ ensure defined

    try:
        res = http_request(
            requests.get,
            f"{config.STATUS_URL}?device_id={device_id}",
            headers=config.HEADERS
        )

        if res.status_code != 200:
            return

        payload = res.json()
        if isinstance(payload, list) and payload:
            payload = payload[0]

        log("\U0001F4E1 BACKEND STATUS \u2193\u2193\u2193", payload, "yellow")

        # ✅ DEVICE ACTIVE CHECK
        if not payload.get("is_active", True):
            log("\u26A0 DEVICE INACTIVE \u2192 SHUTDOWN", "red")
            shutdown_device()
            return

        activate_device_hardware()
        
        # ✅ ONLY TRUST BACKEND CURRENT STATE
        actuators = payload.get("actuators", [])

        for act in actuators:
            pin = act.get("pin")
            name = act.get("type")
            current_state = act.get("current_state", False)
            manual = act.get("manual")

            # ✅ Ưu tiên pin
            if pin is not None:
                key = str(pin).replace("GPIO", "")

            # 🔁 fallback dùng type → GPIO
            elif name in config.TYPE_TO_GPIO:
                key = config.TYPE_TO_GPIO[name]

            else:
                log(f"\u26A0 Unknown actuator {name}", "yellow")
                continue
            
            if key not in config.ACTUATOR_STATES:
                log(f"❌ GPIO {key} NOT IN CONFIG!", "red")
                continue

            # ✅ Update ON/OFF
            state = 1 if current_state else 0
            config.ACTUATOR_STATES[key] = state
        

            # 🔥 handle PWM speed
            if name == "water_pump":
                if "speed" in act:
                    config.PUMP_SPEED[key] = act["speed"]
                elif state == 0:
                    config.PUMP_SPEED[key] = 0  # force OFF
            
            log(f"🔌 GPIO {key}: {'ON' if state else 'OFF'} (BACKEND)", "green")

    except Exception as e:
        log("❌ Command fetch error", str(e), "red")
        
    finally:
        if res:
            res.close()
               

