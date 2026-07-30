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

