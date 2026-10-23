"""Driver for Novation Launchpad Mini mk1/mk2 (not MK3: that one is RGB + SysEx)."""
import mido

NAME = "Launchpad Mini"
COLS, ROWS = 9, 8  # col 8 = round buttons on the right
TOP_CC = 104  # top round buttons: CC 104..111


def color(red=0, green=0):
    """red/green brightness 0-3 -> velocity (flags=12: normal mode)."""
    return 16 * green + red + 12


OFF, RED, GREEN, AMBER, YELLOW = 12, color(3), color(0, 3), color(3, 3), color(2, 3)
DIM_RED, DIM_GREEN = color(1), color(0, 1)


def dim(c):
    """Same hue at minimum brightness."""
    r, g = (c - 12) & 3, ((c - 12) >> 4) & 3
    return color(1 if r else 0, 1 if g else 0)


def _find(names):
    # MK3 matches "Launchpad Mini" too but speaks a different protocol
    return next((n for n in names if NAME in n and "MK3" not in n), None)


class Launchpad:
    def __init__(self):
        self.out = self.inp = None
        self._pads = {}

    @property
    def is_open(self):
        return self.out is not None

    @staticmethod
    def present():
        return _find(mido.get_output_names()) is not None

    def open(self):
        o, i = _find(mido.get_output_names()), _find(mido.get_input_names())
        if not (o and i):
            raise OSError(f"{NAME} not found")
        self.out, self.inp = mido.open_output(o), mido.open_input(i)
        self.clear()

    def close(self, clear=True):
        if clear and self.out:
            try:
                self.clear()
            except Exception:
                pass  # device already gone
        for p in (self.out, self.inp):
            try:
                p and p.close()
            except Exception:
                pass
        self.out = self.inp = None

    def clear(self):
        self.out.send(mido.Message("control_change", control=0, value=0))
        self._pads = {}

    def set_pad(self, x, y, c):
        """x = column 0-8, y = row 0-7; only sends when the colour changed."""
        if self._pads.get((x, y), OFF) != c:
            self.out.send(mido.Message("note_on", note=16 * y + x, velocity=c))
            self._pads[(x, y)] = c

    def set_top(self, i, c):
        if self._pads.get(("top", i), OFF) != c:
            self.out.send(mido.Message("control_change", control=TOP_CC + i, value=c))
            self._pads[("top", i)] = c

    def frame(self, grid):
        """grid: ROWS lists of up to COLS velocities."""
        for y, row in enumerate(grid):
            for x, c in enumerate(row):
                self.set_pad(x, y, c)

    def poll(self):
        """Pending presses as ('pad', x, y) / ('top', i); releases are skipped."""
        for m in self.inp.iter_pending():
            if m.type == "note_on" and m.velocity:
                yield ("pad", m.note % 16, m.note // 16)
            elif m.type == "control_change" and m.value and m.control >= TOP_CC:
                yield ("top", m.control - TOP_CC)
