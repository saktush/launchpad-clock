"""3x4 digit font and a blitter onto a grid of colour values."""

DIGITS = {
    "0": ("111", "101", "101", "111"),
    "1": ("010", "110", "010", "111"),
    "2": ("111", "011", "110", "111"),
    "3": ("111", "011", "001", "111"),
    "4": ("101", "101", "111", "001"),
    "5": ("111", "110", "011", "111"),
    "6": ("100", "111", "101", "111"),
    "7": ("111", "001", "010", "010"),
    "8": ("111", "111", "101", "111"),
    "9": ("111", "101", "111", "001"),
}


def blit_number(grid, text, row, col, c):
    """Draw digits (3 wide, 1 column gap) with top-left at (row, col)."""
    for n, ch in enumerate(text):
        for dy, line in enumerate(DIGITS[ch]):
            for dx, bit in enumerate(line):
                if bit == "1":
                    grid[row + dy][col + n * 4 + dx] = c
