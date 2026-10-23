import argparse
import time
from datetime import datetime

from .font import DIGITS
from .launchpad import DIM_RED, RED, Launchpad, dim
from .screens import ClockScreen

RECONNECT_S = 3
CHARS = {(1, 0): "R", (0, 1): "G", (1, 1): "A"}


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
    pad, bright = Launchpad(), True
    try:
        while True:
            try:
                if not pad.is_open:
                    pad.open()
                    print("Launchpad connected", flush=True)
                for ev in pad.poll():
                    if ev == ("top", 0):
                        bright = not bright
                grid = screen.render(datetime.now())
                if not bright:
                    grid = [[dim(c) for c in row] for row in grid]
                pad.frame(grid)
                pad.set_top(0, RED if bright else DIM_RED)
                if not pad.present():
                    raise OSError("device disconnected")
            except Exception as e:
                if pad.is_open:
                    print(f"Lost Launchpad ({e}); waiting...", flush=True)
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
