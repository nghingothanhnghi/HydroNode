from machine import Pin, I2C
import ssd1306
import time
import config

oled = None

def init_oled():
    """
    Initialize OLED safely.
    Called only once, after power stabilizes.
    """
    global oled
    if oled is None:
        time.sleep(1)  # let ESP32 + OLED power stabilize
        i2c = I2C(0, scl=Pin(22), sda=Pin(21))
        oled = ssd1306.SSD1306_I2C(128, 64, i2c)
        
def _wifi_level(rssi):
    """Map RSSI (dBm) to a 0-4 bar level, like a phone signal icon."""
    if rssi is None:
        return 0
    if rssi >= -55:
        return 4
    elif rssi >= -65:
        return 3
    elif rssi >= -75:
        return 2
    elif rssi >= -85:
        return 1
    return 0


def _draw_wifi_bars(oled, x, y, level, connected):
    bar_w, gap, max_h, n = 2, 1, 8, 4
    for i in range(n):
        h = (i + 1) * max_h // n           # 2, 4, 6, 8 px tall
        bx = x + i * (bar_w + gap)
        by = y + (max_h - h)
        if connected and i < level:
            oled.framebuf.fill_rect(bx, by, bar_w, h, 1)   # filled = active
        else:
            oled.framebuf.rect(bx, by, bar_w, h, 1)        # outline = inactive

def update_oled(device_name, sensor_data, auto_mode, backend_mode, actuators):
    """
    Update OLED display.
    Safe to call repeatedly.
    """
    try:
        init_oled()

        oled.fill(0)

        # Header
        oled.text(device_name[:16], 0, 0)

        # Row 1 – Temperature / Humidity
        oled.text("T:{}C".format(sensor_data.get("temperature", "--")), 0, 12)
        oled.text("H:{}%".format(sensor_data.get("humidity", "--")), 64, 12)


        # Row 1 – Temperature / Humidity
        # Append "?" when the reading is a fallback value (DHT read failed) —
        # otherwise a fake number looks identical to a real one on screen.
        temp_mark = "" if sensor_data.get("temperature_valid", True) else "?"
        hum_mark = "" if sensor_data.get("humidity_valid", True) else "?"
        oled.text("T:{}C{}".format(sensor_data.get("temperature", "--"), temp_mark), 0, 12)
        oled.text("H:{}%{}".format(sensor_data.get("humidity", "--"), hum_mark), 64, 12)        

        # Row 2 – Light / Moisture
        oled.text("L:{}".format(sensor_data.get("light", "--")), 0, 24)
        oled.text("M:{}".format(sensor_data.get("moisture", "--")), 64, 24)

        # Row 3 – Water level + Mode
        oled.text("W:{}".format(sensor_data.get("water_level", "--")), 0, 36)
        # oled.text(
        #     "Mode:{}".format("AUTO" if auto_mode["enabled"] else "MAN"),
        #     64,
        #     36,
        # )
        oled.text("Mode:{}".format(backend_mode.get("mode", "MAN")), 64, 36)

        # ✅ FIX: `actuators` (config.ACTUATOR_STATES) is keyed by GPIO
        # string ("25", "23", ...), not by actuator type ("pump", "fan",
        # ...). The old icon(name) did actuators.get(name), which was
        # always a miss — this line always showed "-" regardless of the
        # real relay state. Resolve type -> GPIO first, then look up
        # both ON/OFF state and the automation reason on that GPIO.
        def icon(actuator_type):
            gpio = config.TYPE_TO_GPIO.get(actuator_type)
            if not gpio or not actuators.get(gpio):
                return "-"
            reason = config.ACTUATOR_REASON.get(gpio, "")
            return "S" if reason == "schedule" else "↑"

        relay_line = "P{} F{} L{} W{}".format(
            icon("pump"),
            icon("fan"),
            icon("light"),
            icon("water_pump"),
        )

        oled.text(relay_line, 0, 48)

        # ================= WIFI / RAIN STATUS =================
        # Rain is a safety-relevant alert, so it takes priority over the
        # WiFi status line when it's actively raining (valid reading only —
        # a failed/uncalibrated sensor should never claim "RAIN").
        rain_valid = sensor_data.get("rain_valid", True)
        rain_detected = sensor_data.get("rain_detected", False)
        rssi = sensor_data.get("_wifi_rssi")
        connected = sensor_data.get("_wifi", "").endswith("OK")
        level = _wifi_level(rssi)
        
        # ================= WIFI STATUS (NEW) =================
        if rain_valid and rain_detected:
            oled.text(
                "RAIN {}%".format(int(sensor_data.get("rain_intensity", 0))),
                0, 56,
            )
        else:
            _draw_wifi_bars(oled, 0, 56, level, connected)
            if rssi is not None:
                oled.text("{}dBm".format(rssi), 18, 56)
            elif not connected:
                oled.text("NO WIFI", 18, 56)
        
        oled.show()

    except Exception as e:
        print("[OLED ERROR]", e)

