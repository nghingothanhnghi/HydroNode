import time, dht
from machine import Pin, ADC

# ---------------- DHT11 ----------------
dht_sensor = dht.DHT11(Pin(14))

# ---------------- EC SENSOR ----------------
ec_adc = ADC(Pin(34))
ec_adc.atten(ADC.ATTN_11DB)   # ~0–3.3V
ec_adc.width(ADC.WIDTH_12BIT)

# ---------------- CONFIG ----------------
ADC_MAX = 4095
VREF = 3.3
EC_CALIBRATION = 2.0
PPM_FACTOR = 500

# ---------------- DHT READ (SAFE) ----------------
def read_dht(retries=3, delay=1):
    """
    Read DHT11 with retry to avoid ETIMEDOUT
    """
    for i in range(retries):
        try:
            dht_sensor.measure()
            temp = dht_sensor.temperature()
            hum = dht_sensor.humidity()
            return temp, hum
        except Exception as e:
            print(f"[!] DHT retry {i+1}/{retries}:", e)
            time.sleep(delay)

    print("[!] DHT FAILED → using fallback")
    return None, None

# ---------------- EC HELPERS ----------------
def read_ec_voltage(samples=30):
    total = 0
    for _ in range(samples):
        total += ec_adc.read()
        time.sleep_ms(10)

    avg = total / samples
    voltage = avg * VREF / ADC_MAX
    return voltage

def temperature_compensation(ec, temperature):
    """
    EC temperature compensation (25°C baseline)
    """
    if temperature is None:
        temperature = 25.0
    return ec / (1 + 0.02 * (temperature - 25))

def read_ec(temperature=None):
    voltage = read_ec_voltage()
    ec = voltage * EC_CALIBRATION
    ec = temperature_compensation(ec, temperature)
    return round(ec, 2)

def ec_to_ppm(ec):
    if ec is None:
        return 0
    return int(ec * PPM_FACTOR)

# ---------------- MAIN SENSOR READ ----------------
def read_sensor_data():
    # --- 1️⃣ Read DHT ---
    temp, hum = read_dht()

    # --- 2️⃣ Fallback nếu lỗi ---
    temp_safe = temp if temp is not None else 25.0
    hum_safe = hum if hum is not None else 60.0

    # --- 3️⃣ Read EC ---
    ec = read_ec(temp_safe)
    ppm = ec_to_ppm(ec)

    # --- 4️⃣ Final payload (KHÔNG BAO GIỜ None) ---
    data = {
        "temperature": float(temp_safe),
        "humidity": float(hum_safe),
        "light": 500,        # TODO: replace with real sensor
        "moisture": 50.0,    # TODO
        "ec": ec,
        "ppm": ppm,
        "water_level": 15.0  # TODO
    }

    # Debug log
    print("[SENSOR]", data)

    return data

