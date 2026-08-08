# auth.py
import urequests as requests
import config
from helper import http_request


def login():
    """
    Exchange username/password for a fresh JWT and store it in
    config.HEADERS["Authorization"] for all subsequent requests.

    Called once at boot (see main.py). Can also be called again later if
    a request comes back 401 — e.g. the DB was wiped and the user was
    recreated mid-session, or the 30-day token expiry was hit while the
    device was running.

    Returns True on success, False otherwise (caller should retry).
    """
    res = None
    try:
        # FastAPI's OAuth2PasswordRequestForm expects form-encoded data,
        # not JSON, for /auth/login.
        body = "username={}&password={}".format(
            config.AUTH_USERNAME, config.AUTH_PASSWORD
        )
        res = http_request(
            requests.post,
            config.LOGIN_URL,
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if res.status_code == 200:
            token = res.json()["access_token"]
            config.HEADERS["Authorization"] = "Bearer " + token
            print("[✓] Login OK, token refreshed")
            return True
        else:
            print("[✗] Login failed:", res.status_code, res.text)
            return False
    except Exception as e:
        print("[!] Login error:", e)
        return False
    finally:
        if res:
            res.close()


def ensure_logged_in(retry_delay=5, max_attempts=None):
    """
    Blocking retry loop for boot time — mirrors the retry pattern already
    used by get_or_register_device() in device.py. Call this before doing
    anything else that needs config.HEADERS["Authorization"].
    """
    import time

    attempts = 0
    while True:
        if login():
            return True
        attempts += 1
        if max_attempts and attempts >= max_attempts:
            return False
        print("[!] Retrying login in", retry_delay, "sec")
        time.sleep(retry_delay)