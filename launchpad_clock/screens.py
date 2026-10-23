"""Screens render a datetime into a ROWS x COLS grid of velocities.

To add a screen (e.g. notification counters): subclass Screen, implement render().
"""
from .font import blit_number
from .launchpad import AMBER, COLS, DIM_RED, GREEN, OFF, ROWS


def blank():
    return [[OFF] * COLS for _ in range(ROWS)]


class Screen:
    def render(self, now):
        raise NotImplementedError


class ClockScreen(Screen):
    """Hours (amber) in rows 0-3, minutes (green) in rows 4-7, seconds dot on the right."""

    def render(self, now):
        g = blank()
        blit_number(g, f"{now.hour:02d}", 0, 0, AMBER)
        blit_number(g, f"{now.minute:02d}", 4, 0, GREEN)
        g[now.second % ROWS][COLS - 1] = DIM_RED  # running dot, one step per second
        return g
