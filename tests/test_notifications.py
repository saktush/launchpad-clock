from launchpad_clock.launchpad import GREEN, OFF, RED, YELLOW
from launchpad_clock.notifications import parse_badge, traffic_light


def test_parse_badge():
    assert [parse_badge(x) for x in ("", "7", "1,234", "23K", "•")] == [0, 7, 1234, 23000, 1]


def test_traffic_light():
    assert [traffic_light(n) for n in (None, 0, 1, 4, 5)] == [OFF, GREEN, YELLOW, YELLOW, RED]
