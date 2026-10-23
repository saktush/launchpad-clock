"""Unread counts from Dock badges (lsappinfo): no tokens, the app just has to be running."""
import re
import subprocess

from .launchpad import GREEN, OFF, RED, YELLOW

APPS = {"Telegram": 1, "Slack": 2}  # app name -> top button index (0 = brightness)
POLL_S = 5
YELLOW_MAX = 4  # 0 green, 1..YELLOW_MAX yellow, more red


def parse_badge(label):
    """'' -> 0, '23K' -> 23000, '1,234' -> 1234, '•' -> 1."""
    m = re.fullmatch(r"\s*(\d[\d,.]*)\s*([KkMm]?)\s*", label)
    if not m:
        return 1 if label.strip() else 0
    n = float(m.group(1).replace(",", ""))
    return int(n * {"": 1, "k": 1e3, "m": 1e6}[m.group(2).lower()])


def badge(app):
    """Unread count, or None when the app is not running."""
    try:
        out = subprocess.run(["lsappinfo", "info", "-only", "StatusLabel", app],
                             capture_output=True, text=True, timeout=2).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    m = re.search(r'"label"="([^"]*)"', out)
    return parse_badge(m.group(1)) if m else None


def traffic_light(n):
    if n is None:
        return OFF
    return GREEN if n == 0 else YELLOW if n <= YELLOW_MAX else RED
