# actuators.py

import urequests as requests
import config
from helper import http_request

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

    # existing_types = set()
    # res = None

    # try:

    #     res = http_request(
    #         requests.get,
    #         f"{config.ACTUATOR_URL}/device/{device_id}",
    #         headers=config.HEADERS
    #     )        

    #     if res.status_code == 200:
    #         existing = res.json()
    #         existing_types = {a["type"] for a in existing}

    # except Exception as e:
    #     print("[!] Could not fetch existing actuators:", e)
    # finally:
    #     if res:
    #         res.close()        

    # to_register = [a for a in actuators if a["type"] not in existing_types]

    # if not to_register:
    #     print("[✓] All actuators already registered for device:", config.DEVICE_CODE)
    #     return

    # res = None
    # try:
    #     res = http_request(
    #         requests.post,
    #         config.ACTUATOR_BULK_URL,
    #         json=to_register,
    #         headers=config.HEADERS
    #     )

    #     if res.status_code in (200, 201):
    #         print(f"[✓] Registered {len(to_register)} actuators for {config.DEVICE_CODE}")
    #     else:
    #         print(f"[!] Bulk registration failed ({res.status_code}): {res.text}")

    # except Exception as e:
    #     print("[!] Bulk registration error:", e)
    # finally:
    #     if res:
    #         res.close()

    existing = []
    res = None
    try:
        res = http_request(
            requests.get,
            f"{config.ACTUATOR_URL}/device/{device_id}",
            headers=config.HEADERS
        )
        if res.status_code == 200:
            existing = res.json()
    except Exception as e:
        print("[!] Could not fetch existing actuators:", e)
    finally:
        if res:
            res.close()

    existing_types = {a["type"] for a in existing}
    # seed the id map with whatever already exists
    for a in existing:
        config.ACTUATOR_IDS[a["type"]] = a["id"]

    to_register = [a for a in actuators if a["type"] not in existing_types]

    if not to_register:
        print("[✓] All actuators already registered for device:", config.DEVICE_CODE)
        print("[✓] Actuator ID map:", config.ACTUATOR_IDS)
        return

    res = None
    try:
        res = http_request(
            requests.post,
            config.ACTUATOR_BULK_URL,
            json=to_register,
            headers=config.HEADERS
        )
        # 🔑 THIS is the block you asked about — right here, replacing the
        # old plain print-only success branch:
        if res.status_code in (200, 201):
            created = res.json()  # list of actuator objects, each with "id" and "type"
            for a in created:
                config.ACTUATOR_IDS[a["type"]] = a["id"]
            print(f"[✓] Registered {len(to_register)} actuators for {config.DEVICE_CODE}")
        else:
            print(f"[!] Bulk registration failed ({res.status_code}): {res.text}")
    except Exception as e:
        print("[!] Bulk registration error:", e)
    finally:
        if res:
            res.close()

    print("[✓] Actuator ID map:", config.ACTUATOR_IDS)   