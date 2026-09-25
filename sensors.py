# sensors.py
import time, dht
from machine import Pin, ADC

# ---------------- DHT11 ----------------
dht_sensor = dht.DHT11(Pin(14))

# ---------------- EC SENSOR ----------------
ec_adc = ADC(Pin(34))
ec_adc.atten(ADC.ATTN_11DB)   # ~0–3.3V
ec_adc.width(ADC.WIDTH_12BIT)

# ---------------- RAIN SENSOR ----------------
# Analog raindrop module (e.g. YL-83 / FC-37 board's "AO" pin).
# GPIO35 is ADC1-capable and input-only, so it doesn't clash with the
# DHT11 (GPIO14) or EC sensor (GPIO34). If your sensor is on a different
# pin, just change this.
#
# ⚠️ No rain sensor is physically wired on this board yet. Reading a
# floating ADC pin and trusting it is exactly what caused rain_detected
# to read stuck True — a floating input reads noise, and that noise
# happened to land below RAIN_DETECT_THRESHOLD. Flip this to True once a
# real sensor is wired to GPIO35 and calibrated.
RAIN_SENSOR_ENABLED = False

rain_adc = ADC(Pin(35)) if RAIN_SENSOR_ENABLED else None
if RAIN_SENSOR_ENABLED:
    rain_adc.atten(ADC.ATTN_11DB)   # ~0–3.3V
    rain_adc.width(ADC.WIDTH_12BIT)

# ---------------- CONFIG ----------------
ADC_MAX = 4095
VREF = 3.3
EC_CALIBRATION = 2.0
PPM_FACTOR = 500

# ⚠️ CALIBRATE THESE on your actual board/sensor:
# - RAIN_ADC_DRY:   raw ADC reading with the sensor plate completely dry
# - RAIN_ADC_WET:   raw ADC reading with the sensor plate fully soaked
# - RAIN_DETECT_THRESHOLD: raw ADC value below which we call it "raining"
# Most raindrop modules read HIGH (near ADC_MAX) when dry and drop as
# water bridges the traces — i.e. voltage falls as rain increases.
RAIN_ADC_DRY = 4095
RAIN_ADC_WET = 1500
RAIN_DETECT_THRESHOLD = 3000

# Fallback values used ONLY when a real reading isn't available.
# These exist so the payload always has a usable number for display/
# control logic, but they are NEVER to be treated as real data — see
# the corresponding "_valid" flags in read_sensor_data().
FALLBACK_TEMP = 25.0
FALLBACK_HUM = 60.0

# ---------------- DHT READ (SAFE) ----------------
def read_dht(retries=3, delay=1):
    """
    Read DHT11 with retry to avoid ETIMEDOUT.
    Returns (temp, hum) on success, or (None, None) if all retries fail.
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

# ---------------- RAIN HELPERS ----------------
def read_rain(samples=10):
    """
    Reads the analog rain sensor.

    Returns (rain_detected: bool, rain_intensity: float 0-100, valid: bool).

    Returns (False, 0.0, False) immediately, without touching the ADC pin,
    when RAIN_SENSOR_ENABLED is False (no sensor physically wired) — this
    is exactly what previously caused a phantom "always raining" reading
    from a floating input.
    """
    if not RAIN_SENSOR_ENABLED:
        return False, 0.0, False
    
    try:
        total = 0
        for _ in range(samples):
            total += rain_adc.read()
            time.sleep_ms(10)
        raw = total / samples
 
        rain_detected = raw < RAIN_DETECT_THRESHOLD
 
        span = RAIN_ADC_DRY - RAIN_ADC_WET
        intensity = 0.0
        if span != 0:
            intensity = (RAIN_ADC_DRY - raw) / span * 100
        intensity = max(0.0, min(100.0, intensity))
 
        return rain_detected, round(intensity, 1), True
 
    except Exception as e:
        print("[!] Rain sensor read error:", e)
        return False, 0.0, False

# ---------------- MAIN SENSOR READ ----------------
def read_sensor_data():
    # --- 1️⃣ Read DHT ---
    temp, hum = read_dht()

    temp_valid = temp is not None
    hum_valid = hum is not None

    # --- 2️⃣ Fallback nếu lỗi ---
    # IMPORTANT: these are placeholder numbers so downstream code (OLED,
    # EC temp-compensation, JSON payload) never has to handle None. They
    # are NOT measurements. Anything that makes a decision based on
    # temperature/humidity must check the matching "_valid" flag first
    # (see control.py::auto_control) rather than trusting the number.
    temp_safe = temp if temp_valid else FALLBACK_TEMP
    hum_safe = hum if hum_valid else FALLBACK_HUM

    # --- 3️⃣ Read EC ---
    ec = read_ec(temp_safe)
    ppm = ec_to_ppm(ec)
    ec_valid = True

    # --- 4️⃣ Read Rain ---
    rain_detected, rain_intensity, rain_valid = read_rain()    

    # --- 4️⃣ Final payload (KHÔNG BAO GIỜ None) ---
    # light / moisture / water_level are still hardcoded stubs (TODO:
    # wire real sensors). Flagging them invalid now means auto_control()
    # and the backend can correctly ignore them instead of silently
    # acting on fabricated numbers.

    data = {
        "temperature": float(temp_safe),
        "temperature_valid": temp_valid,
        "humidity": float(hum_safe),
        "humidity_valid": hum_valid,
        "light": 500,        # TODO: replace with real sensor
        "light_valid": False, # TODO: replace with actual sensor validity
        "moisture": 50.0,    # TODO: replace with real sensor
        "moisture_valid": False, # TODO: replace with actual sensor validity
        "ec": ec,
        "ec_valid": ec_valid,
        "ppm": ppm,
        "water_level": 15.0,  # TODO: replace with real sensor
        "water_level_valid": False,  # TODO: replace with actual sensor validity
        "rain_detected": rain_detected,
        "rain_intensity": rain_intensity,
        "rain_valid": rain_valid
    }

    # Debug log
    print("[SENSOR]", data)

    return data

