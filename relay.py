# relay.py
# from machine import Pin, PWM
# import config
# import time
# 
# 
# 
# MAX_ON_TIME = 10  # seconds (adjust!)
# # _on_since = {}
# 
# # Relay logic (ACTIVE LOW)
# RELAY_ON = 0
# RELAY_OFF = 1
# 
# # ---------------- BUILD GPIO FROM CONFIG ----------------
# 
# relay_pins = {}
# pwm_pins = {}
# 
# for actuator_type, gpio in config.TYPE_TO_GPIO.items():
#     hw_type = config.TYPE_TO_HARDWARE.get(actuator_type, "relay")
# 
#     if hw_type == "relay":
#         relay_pins[gpio] = Pin(int(gpio), Pin.OUT)
#     elif hw_type == "mosfet":
#         pwm_pins[gpio] = PWM(Pin(int(gpio)), freq=1000)
# 
# # Reverse lookup
# GPIO_TO_TYPE = {v: k for k, v in config.TYPE_TO_GPIO.items()}
# 
# # Runtime tracking
# _last_states = {}
# _last_pwm = {}
# 
# # ---------------- VALIDATION ----------------
# def validate_gpio_mapping():
#     print("=== 🔍 GPIO VALIDATION ===")
# 
#     for key in config.ACTUATOR_STATES:
#         if key not in relay_pins and key not in pwm_pins:
#             print(f"⚠ No GPIO wired for {key}")
# 
#     print("=== ✅ VALIDATION DONE ===\n")
# 
# 
# # ---------------- SAFE INIT ----------------
# 
# print("=== ⚡ SAFE GPIO INIT ===")
# 
# for key, pin in relay_pins.items():
# 
#     pin.value(RELAY_OFF)
# 
#     actuator = GPIO_TO_TYPE.get(key, "unknown")
# 
#     print(
#         f"🔌 {actuator.upper()} "
#         f"(GPIO {key}) initialized OFF"
#     )
# 
# for key, pwm in pwm_pins.items():
# 
#     pwm.duty(0)
# 
#     actuator = GPIO_TO_TYPE.get(key, "unknown")
# 
#     print(
#         f"💧 {actuator.upper()} "
#         f"(GPIO {key}) PWM initialized OFF"
#     )
# 
# validate_gpio_mapping()
# 
# # ---------------- MAIN CONTROL ----------------
# 
# def update_relays():
# 
#     # ==================================================
#     # RELAY DEVICES
#     # ==================================================
# 
#     for key, pin in relay_pins.items():
# 
#         actuator = GPIO_TO_TYPE.get(key, "unknown")
# 
#         # Backend logical state
#         # 1 = ON
#         # 0 = OFF
#         state = config.ACTUATOR_STATES.get(key, 0)
# 
#         prev = _last_states.get(key)
# 
#         # Only update on changes
#         if prev != state:
# 
#             # ACTIVE LOW relay logic
#             gpio_value = RELAY_ON if state else RELAY_OFF
# 
#             # Write GPIO
#             pin.value(gpio_value)
# 
#             relay_active = gpio_value == RELAY_ON
# 
#             # ---------------- HUMAN READABLE STATUS ----------------
# 
#             if actuator == "valve":
# 
#                 action = "OPEN" if relay_active else "CLOSED"
#                 emoji = "🚰"
# 
#             elif actuator == "fan":
# 
#                 action = "RUNNING" if relay_active else "STOPPED"
#                 emoji = "🌀"
# 
#             elif actuator == "light":
# 
#                 action = "ON" if relay_active else "OFF"
#                 emoji = "💡"
# 
#             elif actuator == "pump":
# 
#                 action = "ON" if relay_active else "OFF"
#                 emoji = "🚿"
# 
#             else:
# 
#                 action = "ON" if relay_active else "OFF"
#                 emoji = "🔌"
# 
#             # ---------------- DEBUG LOG ----------------
# 
#             print(
#                 f"{emoji} {actuator.upper()} "
#                 f"(GPIO {key}) | "
#                 f"backend={'ON' if state else 'OFF'} | "
#                 f"gpio={'LOW(0)' if gpio_value == 0 else 'HIGH(1)'} | "
#                 f"relay={'ACTIVE' if relay_active else 'INACTIVE'} | "
#                 f"state={action}"
#             )
# 
#             _last_states[key] = state
# 
#     # ==================================================
#     # PWM / MOSFET DEVICES
#     # ==================================================
# 
#     for key, pwm in pwm_pins.items():
# 
#         actuator = GPIO_TO_TYPE.get(key, "unknown")
# 
#         state = config.ACTUATOR_STATES.get(key, 0)
# 
#         speed = config.PUMP_SPEED.get(key, 0)
# 
#         # Safety clamp
#         speed = max(0, min(100, speed))
# 
#         # OFF
#         if state == 0:
# 
#             duty = 0
# 
#         else:
# 
#             # Default full speed
#             if speed == 0:
#                 speed = 100
# 
#             duty = int((speed / 100) * 1023)
# 
#         prev = _last_pwm.get(key)
# 
#         # Only update on change
#         if prev != duty:
# 
#             pwm.duty(duty)
# 
#             print(
#                 f"💧 {actuator.upper()} "
#                 f"(GPIO {key}) | "
#                 f"speed={speed}% | "
#                 f"duty={duty} | "
#                 f"state={'ON' if state else 'OFF'}"
#             )
# 
#             _last_pwm[key] = duty
# 
# 
# # ---------------- TEST GPIO ----------------
# 
# def test_single_gpio(gpio="26"):
# 
#     # ==================================================
#     # RELAY TEST
#     # ==================================================
# 
#     if gpio in relay_pins:
# 
#         pin = relay_pins[gpio]
# 
#         actuator = GPIO_TO_TYPE.get(gpio, "unknown")
# 
#         print(f"\n=== 🧪 TEST RELAY GPIO {gpio} ({actuator}) ===")
# 
#         while True:
# 
#             print(
#                 f"🔛 {actuator.upper()} | "
#                 f"gpio=LOW(0) | "
#                 f"relay=ACTIVE"
#             )
# 
#             pin.value(RELAY_ON)
# 
#             time.sleep(2)
# 
#             print(
#                 f"🔴 {actuator.upper()} | "
#                 f"gpio=HIGH(1) | "
#                 f"relay=INACTIVE"
#             )
# 
#             pin.value(RELAY_OFF)
# 
#             time.sleep(2)
# 
#     # ==================================================
#     # PWM TEST
#     # ==================================================
# 
#     elif gpio in pwm_pins:
# 
#         pwm = pwm_pins[gpio]
# 
#         actuator = GPIO_TO_TYPE.get(gpio, "unknown")
# 
#         print(f"\n=== 🧪 TEST PWM GPIO {gpio} ({actuator}) ===")
# 
#         while True:
# 
#             print(f"💧 {actuator.upper()} → 30%")
# 
#             pwm.duty(int(0.3 * 1023))
# 
#             time.sleep(3)
# 
#             print(f"💧 {actuator.upper()} → 70%")
# 
#             pwm.duty(int(0.7 * 1023))
# 
#             time.sleep(3)
# 
#             print(f"💧 {actuator.upper()} → OFF")
# 
#             pwm.duty(0)
# 
#             time.sleep(3)
# 
#     else:
# 
#         print(f"❌ GPIO {gpio} not found")


# relay.py
from machine import Pin, PWM
import config
import time



# Per-actuator max continuous ON time (seconds).
# Must be LONGER than the longest schedule/interval you expect for that actuator,
# otherwise this safety net will fight your schedule.
MAX_ON_TIME = {
    "pump": 300,        # 5 min
    "water_pump": 900,  # 15 min
    "valve": 1200,      # 20 min — above your 15-min irrigation window
    "fan": 3600,
    "light": 43200,
}
DEFAULT_MAX_ON_TIME = 600  # fallback for any actuator type not listed above
# _on_since = {}

# Relay logic (ACTIVE LOW)
RELAY_ON = 0
RELAY_OFF = 1

# ---------------- BUILD GPIO FROM CONFIG ----------------

relay_pins = {}
pwm_pins = {}

for actuator_type, gpio in config.TYPE_TO_GPIO.items():
    hw_type = config.TYPE_TO_HARDWARE.get(actuator_type, "relay")

    if hw_type == "relay":
        relay_pins[gpio] = Pin(int(gpio), Pin.OUT)
    elif hw_type == "mosfet":
        pwm_pins[gpio] = PWM(Pin(int(gpio)), freq=1000)

# Reverse lookup
GPIO_TO_TYPE = {v: k for k, v in config.TYPE_TO_GPIO.items()}

# Runtime tracking
_last_states = {}
_last_pwm = {}
_on_since = {}   # key -> timestamp when this actuator turned ON (relay OR pwm)

# ---------------- VALIDATION ----------------
def validate_gpio_mapping():
    print("=== 🔍 GPIO VALIDATION ===")

    for key in config.ACTUATOR_STATES:
        if key not in relay_pins and key not in pwm_pins:
            print(f"⚠ No GPIO wired for {key}")

    print("=== ✅ VALIDATION DONE ===\n")


# ---------------- SAFE INIT ----------------

print("=== ⚡ SAFE GPIO INIT ===")

for key, pin in relay_pins.items():
    pin.value(RELAY_OFF)
    actuator = GPIO_TO_TYPE.get(key, "unknown")
    print(
        f"🔌 {actuator.upper()} "
        f"(GPIO {key}) initialized OFF"
    )

for key, pwm in pwm_pins.items():
    pwm.duty(0)
    actuator = GPIO_TO_TYPE.get(key, "unknown")
    print(
        f"💧 {actuator.upper()} "
        f"(GPIO {key}) PWM initialized OFF"
    )

validate_gpio_mapping()


def _enforce_max_on_time():
    now = time.time()
    for key, started in list(_on_since.items()):
        actuator = GPIO_TO_TYPE.get(key, "unknown")
        limit = MAX_ON_TIME.get(actuator, DEFAULT_MAX_ON_TIME)
        if now - started > limit:
            print(
                f"\u23F1 SAFETY CUTOFF: {actuator.upper()} (GPIO {key}) "
                f"exceeded MAX_ON_TIME={limit}s -> forcing OFF"
            )
            config.ACTUATOR_STATES[key] = 0
            if key in config.PUMP_SPEED:
                config.PUMP_SPEED[key] = 0


# ---------------- MAIN CONTROL ----------------

def update_relays():

    _enforce_max_on_time()

    # ==================================================
    # RELAY DEVICES
    # ==================================================

    for key, pin in relay_pins.items():

        actuator = GPIO_TO_TYPE.get(key, "unknown")
        # Backend logical state
        # 1 = ON
        # 0 = OFF
        state = config.ACTUATOR_STATES.get(key, 0)
        prev = _last_states.get(key)

        # Only update on changes
        if prev != state:

            # ACTIVE LOW relay logic
            gpio_value = RELAY_ON if state else RELAY_OFF
            # Write GPIO
            pin.value(gpio_value)
            relay_active = gpio_value == RELAY_ON

            # ---------------- HUMAN READABLE STATUS ----------------

            if actuator == "valve":

                action = "OPEN" if relay_active else "CLOSED"
                emoji = "🚰"

            elif actuator == "fan":

                action = "RUNNING" if relay_active else "STOPPED"
                emoji = "🌀"

            elif actuator == "light":

                action = "ON" if relay_active else "OFF"
                emoji = "💡"

            elif actuator == "pump":

                action = "ON" if relay_active else "OFF"
                emoji = "🚿"

            else:

                action = "ON" if relay_active else "OFF"
                emoji = "🔌"

            # ---------------- DEBUG LOG ----------------

            print(
                f"{emoji} {actuator.upper()} "
                f"(GPIO {key}) | "
                f"backend={'ON' if state else 'OFF'} | "
                f"gpio={'LOW(0)' if gpio_value == 0 else 'HIGH(1)'} | "
                f"relay={'ACTIVE' if relay_active else 'INACTIVE'} | "
                f"state={action}"
            )

            _last_states[key] = state

            if state:
                _on_since[key] = time.time()
            else:
                _on_since.pop(key, None)            

    # ==================================================
    # PWM / MOSFET DEVICES
    # ==================================================

    for key, pwm in pwm_pins.items():

        actuator = GPIO_TO_TYPE.get(key, "unknown")
        state = config.ACTUATOR_STATES.get(key, 0)
        speed = config.PUMP_SPEED.get(key, 0)
        # Safety clamp
        speed = max(0, min(100, speed))

        # OFF
        if state == 0:

            duty = 0

        else:

            # Default full speed
            if speed == 0:
                speed = 100
            duty = int((speed / 100) * 1023)

        prev = _last_pwm.get(key)

        # Only update on change
        if prev != duty:
            pwm.duty(duty)
            print(
                f"💧 {actuator.upper()} "
                f"(GPIO {key}) | "
                f"speed={speed}% | "
                f"duty={duty} | "
                f"state={'ON' if state else 'OFF'}"
            )
            _last_pwm[key] = duty

            if duty > 0:
                _on_since.setdefault(key, time.time())
            else:
                _on_since.pop(key, None)

# ---------------- TEST GPIO ----------------

def test_single_gpio(gpio="26"):

    # ==================================================
    # RELAY TEST
    # ==================================================

    if gpio in relay_pins:
        pin = relay_pins[gpio]
        actuator = GPIO_TO_TYPE.get(gpio, "unknown")
        print(f"\n=== 🧪 TEST RELAY GPIO {gpio} ({actuator}) ===")

        while True:
            print(
                f"🔛 {actuator.upper()} | "
                f"gpio=LOW(0) | "
                f"relay=ACTIVE"
            )
            pin.value(RELAY_ON)
            time.sleep(2)
            print(
                f"🔴 {actuator.upper()} | "
                f"gpio=HIGH(1) | "
                f"relay=INACTIVE"
            )
            pin.value(RELAY_OFF)
            time.sleep(2)

    # ==================================================
    # PWM TEST
    # ==================================================

    elif gpio in pwm_pins:
        pwm = pwm_pins[gpio]
        actuator = GPIO_TO_TYPE.get(gpio, "unknown")
        print(f"\n=== 🧪 TEST PWM GPIO {gpio} ({actuator}) ===")

        while True:
            print(f"💧 {actuator.upper()} → 30%")
            pwm.duty(int(0.3 * 1023))
            time.sleep(3)
            print(f"💧 {actuator.upper()} → 70%")
            pwm.duty(int(0.7 * 1023))
            time.sleep(3)
            print(f"💧 {actuator.upper()} → OFF")
            pwm.duty(0)
            time.sleep(3)

    else:
        print(f"❌ GPIO {gpio} not found")


