# wifi.py
import network
import time
import config
import ubinascii
import socket

# ==================================================
# WIFI SCAN
# ==================================================
def scan_wifi():

    wlan = network.WLAN(network.STA_IF)

    try:
        wlan.active(False)
        time.sleep(1)

        wlan.active(True)
        time.sleep(2)

        print("\n========================================")
        print("📡 WIFI SCAN")
        print("========================================")
        print("WiFi Active:", wlan.active())

        aps = wlan.scan()

        print("AP COUNT:", len(aps))

        for ap in aps:

            try:
                ssid = ap[0].decode()

                bssid = ":".join(
                    "{:02X}".format(x)
                    for x in ap[1]
                )

                channel = ap[2]
                rssi = ap[3]

                print(
                    "SSID:", ssid,
                    "| CH:", channel,
                    "| RSSI:", rssi,
                    "| BSSID:", bssid
                )

            except Exception as e:
                print("AP Parse Error:", e)

    except Exception as e:
        print("❌ Scan Error:", repr(e))

    print("========================================\n")


# ==================================================
# WIFI CONNECT
# ==================================================
def connect_wifi():

    scan_wifi()

    wlan = network.WLAN(network.STA_IF)

    try:
        wlan.active(False)
        time.sleep(1)

        wlan.active(True)
        time.sleep(2)

        try:
            wlan.disconnect()
        except:
            pass

        time.sleep(1)

    except Exception as e:
        print("WiFi Init Error:", repr(e))

    print("\n========================================")
    print("📶 WIFI CONNECTION")
    print("========================================")
    print("SSID:", config.SSID)
    print("Backend:", config.FASTAPI_URL)

    start_time = time.time()

    if not wlan.isconnected():

        print("[WiFi] Connecting...")

        try:

            wlan.connect(
                config.SSID,
                config.PASSWORD
            )

        except Exception as e:

            print("❌ connect() failed:", repr(e))
            raise

        retry = 0

        while not wlan.isconnected():

            retry += 1

            try:
                status = wlan.status()
            except:
                status = "UNKNOWN"       
            
            status_map = {
                1000: "IDLE",
                1001: "CONNECTING",
                1010: "GOT_IP",
                202: "AUTH_FAIL",
                201: "NO_AP_FOUND",
            }

            print(
                "[WiFi] Attempt",
                retry,
                "| Status:",
                status_map.get(status, status)
            )

            time.sleep(1)

            if retry > 20:

                print(
                    "[WiFi] Timeout",
                    "| Status:",
                    status
                )

                try:
                    wlan.disconnect()
                except:
                    pass

                time.sleep(2)

                try:

                    wlan.connect(
                        config.SSID,
                        config.PASSWORD
                    )

                except Exception as e:

                    print(
                        "Reconnect Error:",
                        repr(e)
                    )

                retry = 0

    connect_time = round(
        time.time() - start_time,
        1
    )

    ip, subnet, gateway, dns = wlan.ifconfig()

    print("\n✅ WIFI CONNECTED")
    print("----------------------------------------")
    print("DHCP INFO")
    print("IP       :", ip)
    print("Subnet   :", subnet)
    print("Gateway  :", gateway)
    print("DNS      :", dns)

    try:

        mac = ":".join(
            "{:02X}".format(x)
            for x in wlan.config("mac")
        )

        print("MAC      :", mac)

    except:
        pass

    try:

        bssid = ubinascii.hexlify(
            wlan.config("bssid"),
            ":"
        ).decode().upper()

        print("AP BSSID :", bssid)

    except Exception as e:

        print("BSSID Error:", e)

    try:

        print(
            "RSSI     :",
            wlan.status("rssi"),
            "dBm"
        )

    except:
        pass

    print("Time     :", connect_time, "sec")

    backend_ip = (
        config.FASTAPI_URL
        .replace("http://", "")
        .split(":")[0]
    )

    print("----------------------------------------")
    print("Backend IP:", backend_ip)

    if (
        ip.startswith("192.168.1.")
        and
        backend_ip.startswith("192.168.1.")
    ):
        print("✅ Same subnet")
    else:
        print("❌ Different subnet")

    print("========================================\n")

    return wlan

# ==================================================
# TEST GATEWAY
# ==================================================
def test_gateway():

    wlan = network.WLAN(network.STA_IF)

    if not wlan.isconnected():

        print("❌ WiFi not connected")
        return

    gateway = wlan.ifconfig()[2]

    print("\n========================================")
    print("🌐 GATEWAY TEST")
    print("========================================")
    print("Gateway :", gateway)

    try:

        addr = socket.getaddrinfo(
            gateway,
            80
        )[0][-1]

        s = socket.socket()

        s.settimeout(5)

        start = time.time()

        s.connect(addr)

        latency = round(
            (time.time() - start) * 1000,
            1
        )

        print("✅ Gateway reachable")
        print("Latency :", latency, "ms")

        s.close()

    except Exception as e:

        print("❌ Gateway unreachable")
        print("Error :", e)

    print("========================================\n")


# ==================================================
# TEST BACKEND
# ==================================================
def test_backend():

    try:

        host = (
            config.FASTAPI_URL
            .replace("http://", "")
            .split(":")[0]
        )

        port = int(
            config.FASTAPI_URL
            .split(":")[-1]
        )

        print("\n========================================")
        print("🌐 BACKEND TEST")
        print("========================================")
        print("Host :", host)
        print("Port :", port)

        addr = socket.getaddrinfo(
            host,
            port
        )[0][-1]

        print("Resolved :", addr)

        s = socket.socket()
        s.settimeout(5)

        start = time.time()

        s.connect(addr)

        latency = round(
            (time.time() - start) * 1000,
            1
        )

        print("✅ Backend reachable")
        print("Latency :", latency, "ms")

        s.close()

    except Exception as e:

        print("❌ Backend unreachable")
        print("Error :", e)

    print("========================================\n")

