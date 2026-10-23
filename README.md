# launchpad-clock

Turns a Novation Launchpad Mini into a small clock display (macOS).

- Hours (amber) in rows 0–3, minutes (green) in rows 4–7, 3×4 pixel font.
- A red dot runs down the right-hand round buttons, one step per second.
- Top-left round button (CC 104) toggles bright/dim.
- Only changed pads are sent. Unplug the device and it waits and reconnects.

**Supported:** Launchpad Mini mk1 and mk2 (same MIDI protocol). Not MK3 (RGB/SysEx).

## Install

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Run

```bash
.venv/bin/python -m launchpad_clock                       # on the device, Ctrl+C to quit
.venv/bin/python -m launchpad_clock --simulate            # live ASCII clock in the terminal
.venv/bin/python -m launchpad_clock --simulate --at 23:59 # one frame for a given time
.venv/bin/python -m launchpad_clock --font                # all digits + sample times
```

Tests: `.venv/bin/pip install pytest && .venv/bin/python -m pytest`

## Layout

- `launchpad_clock/launchpad.py` – MIDI driver (`set_pad`, `clear`, `frame`, `poll`)
- `launchpad_clock/font.py` – 3×4 digit font
- `launchpad_clock/screens.py` – screens (`ClockScreen`); add new ones by subclassing `Screen`

## License

MIT
