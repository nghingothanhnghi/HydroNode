# control.py
import urequests as requests
import config
from helper import log, http_request
from device import shutdown_device, activate_device as activate_device_hardware

def auto_control(data):

    def set_state(actuator_type, condition):
        gpio = config.TYPE_TO_GPIO.get(actuator_type)
        
        # ❌ DO NOT override if backend already ON
        if gpio and config.ACTUATOR_STATES.get(gpio) == 0:
            config.ACTUATOR_STATES[gpio] = 1 if condition else 0

    if data["temperature"] is not None:
        set_state("fan", data["temperature"] > 28)

    if data["moisture"] is not None:
        set_state("pump", data["moisture"] < 40)

    if data["light"] is not None:
        set_state("light", data["light"] < 300)

    if data["water_level"] is not None:
        set_state("water_pump", data["water_level"] < 10)

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
               

