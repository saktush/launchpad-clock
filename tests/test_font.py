from datetime import datetime

from launchpad_clock.font import DIGITS
from launchpad_clock.screens import ClockScreen


def test_digits_shape_and_distinct():
    assert all(len(d) == 4 and all(len(r) == 3 for r in d) for d in DIGITS.values())
    assert len(set(DIGITS.values())) == 10


def test_clock_fits_and_splits_colours():
    g = ClockScreen().render(datetime(2026, 1, 1, 23, 59, 0))
    assert len(g) == 8 and all(len(r) == 9 for r in g)
    assert any(c == 63 for r in g[:4] for c in r) and any(c == 60 for r in g[4:] for c in r)
