# device.py
import urequests as requests
import config
import time
import machine
from relay import relay_pins, update_relays
from helper import http_request


def get_or_register_device():
    res = None
    try:
        res = http_request(requests.get, config.DEVICE_URL, headers=config.HEADERS)
        if res.status_code == 200:
            for device in res.json():
                if device.get("device_id") == config.DEVICE_CODE:
                    print("[✓] Device found:", config.DEVICE_CODE)
                    return device["id"], device["name"]
    except Exception as e:
        print("[!] Failed to fetch devices:", e)
    finally:
        if res:
            res.close()

    payload = {
        "device_id": config.DEVICE_CODE, # DEVICE_CODE got from ESP32, auto generate when connected to BackEnd, added to DB for device_id
        "name": "Nghi Ngo ESP32 Ex",
        "location": "Hydroponics Lab",
        "type": "ESP32",
        "is_active": True,
        "client_id": config.CLIENT_ID,
        "thresholds": {},
        "user_id": config.USER_ID,
    }

    res = None
    try:
        res = http_request(
            requests.post, config.DEVICE_URL, json=payload, headers=config.HEADERS
        )
        if res.status_code in (200, 201):
            device = res.json()
            print("[✓] Device registered:", config.DEVICE_CODE)
            return device["id"], device["name"]
        else:
            print("[✗] Device registration failed:", res.status_code, res.text)
    except Exception as e:
        print("[!] Register device error:", e)
    finally:
        if res:
            res.close()
 
    return None, None

def shutdown_device():
    """Turn off all actuators and put ESP32 into deep sleep."""
    print("[⚡] Shutting down device...")
    try:
        # Turn off all relays
        for pin in relay_pins.values():
            pin.value(0)
        update_relays()  # Ensure the states are applied

        time.sleep(0.5)  # give some time for relays to settle
        print("[⚡] Device entering deep sleep")
        machine.deepsleep()
    except Exception as e:
        print("[!] Shutdown error:", e)


def activate_device():
    """Reactivate device (simply prints message, relays remain controlled by AUTO_MODE)."""
    print("[⚡] Device activated")
    if config.AUTO_MODE.get("enabled", False):
        # Normally relays will be managed in main.py auto_control
        update_relays()

