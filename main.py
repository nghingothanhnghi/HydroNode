from helper import http_request
import time, machine, urequests as requests
from machine import WDT
from wifi import connect_wifi, test_backend, test_gateway
from device import get_or_register_device
from actuators import register_actuators
from sensors import read_sensor_data
from oled_display import update_oled
from relay import update_relays, test_single_gpio
from control import auto_control, check_commands
import config


# ---------------- WATCHDOG ----------------
# NOTE: once started, the ESP32 WDT cannot be disabled or re-configured —
# it will reset the device if `wdt.feed()` isn't called within `timeout`.
# 30s gives generous headroom over one loop iteration (~0.2-1s normally,
# or a bit more if WiFi/backend calls are slow) while still guaranteeing
# recovery from a true hang.
wdt = WDT(timeout=30000)  # ms


def main():
    print("=== ESP32 BOOT ===")
    print("DEVICE_CODE:", config.DEVICE_CODE)
    time.sleep(2)  # allow hardware to stabilize
    wdt.feed()
    
    # 1️⃣ Connect to WiFi (after short delay)
    wlan = connect_wifi()
    wdt.feed()
    test_gateway()
    test_backend()
    
    device_id, device_name = None, None
    while not device_id:
        device_id, device_name = get_or_register_device()
        wdt.feed()
        if not device_id:
            print("[✗] No device ID, retrying in", config.RETRY_DELAY, "sec")
            time.sleep(config.RETRY_DELAY)
            wdt.feed()

    # 2️⃣ Register actuators in backend
    register_actuators(device_id)
    wdt.feed()

    last_send = 0
    last_oled = 0 
    last_wifi_check = 0
    wifi_status = "WiFi: OK"
    
    while True:
        wdt.feed()
        now = time.time()
        # 3️⃣ Safer WiFi reconnect with OLED status
        if not wlan.isconnected():
            wifi_status = "WiFi: LOST"
            if now - last_wifi_check > 5:
                print("[WiFi] Disconnected, reconnecting...")
                last_wifi_check = now
                wlan = connect_wifi()
                wdt.feed()
        else:
            wifi_status = "WiFi: OK"
            
        sensor_data = read_sensor_data()
        sensor_data["_wifi"] = wifi_status
        
        # 4️⃣ Automatic control
#         if config.AUTO_MODE["enabled"]:
#             auto_control(sensor_data)
        
        # 5️⃣ Send sensor data periodically
        if now - last_send >= config.SEND_INTERVAL:
            last_send = now
            payload = {
                "device_id": config.DEVICE_CODE,
                "client_id": config.CLIENT_ID,
                "data": sensor_data
            }

            res = None
            try:
                res = http_request(
                    requests.post,
                    config.SENSOR_URL,
                    json=payload,
                    headers=config.HEADERS
                )
                print("[→] Sent data:", res.status_code, payload)

            except Exception as e:
                print("[!] Send error:", e)
            finally:
                if res:
                    res.close()

            wdt.feed()
            check_commands(device_id)
            wdt.feed()

        # 6️⃣ Update display and relays
        if now - last_oled >= 1:
            update_oled(
                device_name,
                sensor_data,
                config.AUTO_MODE,
                config.ACTUATOR_STATES,
            )
            last_oled = now
        
        # 7️⃣ Apply relay states to GPIO
        update_relays()   # <-- after check_commands()    

        time.sleep(0.2)
        # run relays at lower frequency
#         if now - last_oled >= 1:
#             update_relays()

try:
    main()
    
except Exception as e:
    print("[BOOT ERROR]", e)
    time.sleep(5)
    print("[BOOT ERROR] Resetting device...")
    machine.reset()    
    
# =========================
# 🔥 ENTRY POINT
# =========================

# if __name__ == "__main__":
# 
#     TEST_MODE = True
# 
#     try:
# 
#         if TEST_MODE:
# 
#             print("=== GPIO TEST MODE ===")
# 
#             test_single_gpio("26")
# 
#         else:
# 
#             main()
# 
#     except Exception as e:
# 
#         print("[BOOT ERROR]", e)
# 
#         time.sleep(5)


