import ujson as json

# Simple ANSI color codes
COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "cyan": "\033[96m",
    "reset": "\033[0m"
}

def pretty(obj):
    """Return pretty-formatted JSON with indentation (Micropython safe)."""
    try:
        return json.dumps(obj, indent=4)
    except:
        # fallback for non-serializable objects
        return str(obj)

def log(title, data=None, color="cyan"):
    """Formatted logging with colored title + pretty JSON body."""
    c = COLORS.get(color, COLORS["cyan"])
    r = COLORS["reset"]

    print("\n" + c + "=== " + title + " ===" + r)

    if data is not None:
        print(pretty(data))

def http_request(method, url, timeout=5, **kwargs):
    """
    Wrapper around urequests.get / urequests.post (etc) that enforces a
    socket timeout so a stalled backend can't hang the whole main loop.
 
    Usage:
        res = http_request(requests.get, config.DEVICE_URL, headers=config.HEADERS)
        res = http_request(requests.post, config.DEVICE_URL, json=payload, headers=config.HEADERS)
 
    Some builds of urequests accept a `timeout=` kwarg directly; others
    don't. We try the modern signature first and fall back gracefully so
    this works across firmware/library versions without crashing.
    """
    try:
        return method(url, timeout=timeout, **kwargs)
    except TypeError:
        # Installed urequests doesn't support timeout=; fall back to a
        # plain call. Still far better than nothing, and cheap to upgrade
        # later by vendoring a urequests build that supports timeouts.
        return method(url, **kwargs)