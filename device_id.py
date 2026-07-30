# device_id.py
import network
import ubinascii

def get_device_code():
    """
    Generate a stable, unique device code from ESP32 MAC address.
    Example: esp32_24:6f:28:aa:bb:cc
    """
    wlan = network.WLAN(network.STA_IF)
    mac = ubinascii.hexlify(wlan.config('mac'), ':').decode()
    return "esp32_" + mac

