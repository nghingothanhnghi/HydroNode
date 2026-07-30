# actuators.py

import urequests as requests
import config

def register_actuators(device_id):
    actuators = [
        {
            "name": "Pump",
            "type": "pump",
            "port": 1,
            "pin": config.TYPE_TO_GPIO["pump"],
            "device_id": device_id
        },
        {
            "name": "Fan",
            "type": "fan",
            "port": 2,
            "pin": config.TYPE_TO_GPIO["fan"],
            "device_id": device_id
        },
        {
            "name": "Light",
            "type": "light",
            "port": 3,
            "pin": config.TYPE_TO_GPIO["light"],
            "device_id": device_id
        },
        {
            "name": "Water Pump",
            "type": "water_pump",
            "port": 4,
            "pin": config.TYPE_TO_GPIO["water_pump"],
            "device_id": device_id
        },
        {
            "name": "Valve",
            "type": "valve",
            "port": 5,
            "pin": config.TYPE_TO_GPIO["valve"],
            "device_id": device_id
        },
    ]

    existing_types = set()

    try:
        res = requests.get(
            f"{config.ACTUATOR_URL}/device/{device_id}",
            headers=config.HEADERS
        )

        if res.status_code == 200:
            existing = res.json()
            existing_types = {a["type"] for a in existing}

        res.close()  # ✅ IMPORTANT

    except Exception as e:
        print("[!] Could not fetch existing actuators:", e)

    to_register = [a for a in actuators if a["type"] not in existing_types]

    if not to_register:
        print("[✓] All actuators already registered for device:", config.DEVICE_CODE)
        return

    try:
        res = requests.post(
            config.ACTUATOR_BULK_URL,
            json=to_register,
            headers=config.HEADERS
        )

        if res.status_code in (200, 201):
            print(f"[✓] Registered {len(to_register)} actuators for {config.DEVICE_CODE}")
        else:
            print(f"[!] Bulk registration failed ({res.status_code}): {res.text}")

        res.close()  # ✅ IMPORTANT

    except Exception as e:
        print("[!] Bulk registration error:", e)
