# wifi.py
import network, time
import config

import ubinascii
import socket

def scan_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    print("\n========================================")
    print("📡 WIFI SCAN")
    print("========================================")

    try:

        aps = wlan.scan()

        for ap in aps:

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
        print("Scan error:", e)

    print("========================================\n")

def connect_wifi():
    
    # Scan nearby APs first
    scan_wifi()
    
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("\n========================================")
    print("📶 WIFI CONNECTION")
    print("========================================")
    print("SSID:", config.SSID)
    print("Backend:", config.FASTAPI_URL)
    
    start_time = time.time()
    
    if not wlan.isconnected():
        
        print("[WiFi] Connecting...")
        wlan.connect(config.SSID, config.PASSWORD)
        
        retry = 0
        
        while not wlan.isconnected():
            
            retry += 1
            print("[WiFi] Attempt", retry)
            
            time.sleep(1)
            
            if retry > 20:
           
                print("[WiFi] Timeout → reconnecting")

                wlan.disconnect()
                time.sleep(2)

                wlan.connect(
                    config.SSID,
                    config.PASSWORD,
                )
                
                retry = 0
    
    connect_time = round(time.time() - start_time, 1)

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

    # ADD THIS BLOCK
    try:
        bssid = ubinascii.hexlify(
            wlan.config("bssid"),
            ":"
        ).decode().upper()

        print("AP BSSID :", bssid)

    except Exception as e:
        print("BSSID error:", e)

    try:
        print("RSSI     :", wlan.status("rssi"), "dBm")
    except:
        pass

    print("Time     :", connect_time, "sec")

    # Check backend subnet
    backend_ip = (
        config.FASTAPI_URL
        .replace("http://", "")
        .split(":")[0]
    )

    print("----------------------------------------")
    print("Backend IP:", backend_ip)

    if ip.startswith("192.168.1.") and backend_ip.startswith("192.168.1."):
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

