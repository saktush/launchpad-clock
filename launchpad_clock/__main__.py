import argparse
import signal
import time
from datetime import datetime

from .font import DIGITS
from .launchpad import DIM_RED, RED, Launchpad, dim
from .notifications import APPS, POLL_S, badge, traffic_light
from .screens import ClockScreen

RECONNECT_S = 3
WAKE_GAP_S = 5  # loop ticks every 0.1s; a longer wall-clock gap means the Mac slept
REFRESH_S = 30  # reopen the port and resend every LED, in case the handle or device state died silently
CHARS = {(1, 0): "R", (0, 1): "G", (1, 1): "A"}


def log(msg):
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} {msg}", flush=True)


def ascii_grid(grid):
    def ch(c):
        rg = (min((c - 12) & 3, 1), min(((c - 12) >> 4) & 3, 1))
        return CHARS.get(rg, ".")
    return "\n".join(" ".join(ch(c) for c in row[:-1]) + " | " + ch(row[-1]) for row in grid)


def simulate(screen, at):
    if at:
        h, m = map(int, at.split(":"))
        print(ascii_grid(screen.render(datetime(2026, 1, 1, h, m, 0))))
        return
    try:
        while True:
            print("\033[2J\033[H" + ascii_grid(screen.render(datetime.now())), flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        pass


def font_sheet(screen):
    rows = ["  ".join(DIGITS[d][r].replace("0", ".").replace("1", "#") for d in "0123456789") for r in range(4)]
    print("0    1    2    3    4    5    6    7    8    9")
    print("\n".join(rows))
    for t in ("08:15", "23:59", "12:34", "07:06"):
        print(f"\n{t}")
        simulate(screen, t)


def run(screen):
    signal.signal(signal.SIGTERM, signal.default_int_handler)  # launchctl stop -> clear LEDs too
    pad, bright = Launchpad(), True
    counts, polled = {}, 0.0
    last_tick = last_refresh = time.time()
    try:
        while True:
            try:
                now = time.time()
                if now - last_tick > WAKE_GAP_S:
                    # CoreMIDI endpoints can be recreated on wake while the old handle silently drops writes
                    log(f"Woke after {now - last_tick:.0f}s gap; reopening port")
                    pad.close(clear=False)
                    polled = 0.0
                last_tick = now
                if not pad.is_open:
                    pad.open()
                    last_refresh = now
                    log("Launchpad connected")
                elif now - last_refresh >= REFRESH_S:
                    # display sleep / USB re-enumeration does not freeze us (no gap) yet kills the handle
                    pad.close(clear=False)
                    pad.open(clear=False)
                    last_refresh = now
                for ev in pad.poll():
                    if ev == ("top", 0):
                        bright = not bright
                grid = screen.render(datetime.now())
                if not bright:
                    grid = [[dim(c) for c in row] for row in grid]
                pad.frame(grid)
                pad.set_top(0, RED if bright else DIM_RED)
                if time.monotonic() - polled >= POLL_S:
                    counts, polled = {a: badge(a) for a in APPS}, time.monotonic()
                for app, i in APPS.items():
                    c = traffic_light(counts[app])
                    pad.set_top(i, c if bright else dim(c))
                if not pad.present():
                    raise OSError("device disconnected")
            except Exception as e:
                if pad.is_open:
                    log(f"Lost Launchpad ({e}); waiting...")
                pad.close(clear=False)
                time.sleep(RECONNECT_S)
                continue
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        pad.close()


def main():
    ap = argparse.ArgumentParser(description="Clock on a Novation Launchpad Mini")
    ap.add_argument("--simulate", action="store_true", help="draw in the terminal, no device")
    ap.add_argument("--at", metavar="HH:MM", help="with --simulate: print this time once")
    ap.add_argument("--font", action="store_true", help="print all digits and sample times")
    a = ap.parse_args()
    screen = ClockScreen()
    if a.font:
        font_sheet(screen)
    elif a.simulate:
        simulate(screen, a.at)
    else:
        run(screen)


if __name__ == "__main__":
    main()
