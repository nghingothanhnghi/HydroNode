from machine import Pin, I2C
import ssd1306
import time

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

def update_oled(device_name, sensor_data, auto_mode, actuators):
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

        # Row 2 – Light / Moisture
        oled.text("L:{}".format(sensor_data.get("light", "--")), 0, 24)
        oled.text("M:{}".format(sensor_data.get("moisture", "--")), 64, 24)

        # Row 3 – Water level + Mode
        oled.text("W:{}".format(sensor_data.get("water_level", "--")), 0, 36)
        oled.text(
            "Mode:{}".format("AUTO" if auto_mode["enabled"] else "MAN"),
            64,
            36,
        )

        def icon(name):
            return "↑" if actuators.get(name) else "-"

        relay_line = "P{} F{} L{} W{}".format(
            icon("pump"),
            icon("fan"),
            icon("light"),
            icon("water_pump"),
        )

        oled.text(relay_line, 0, 48)
        
        # ================= WIFI STATUS (NEW) =================
        wifi_status = sensor_data.get("_wifi", "")
        if wifi_status:
            oled.text(wifi_status[:12], 0, 56)
        
        oled.show()

    except Exception as e:
        print("[OLED ERROR]", e)

