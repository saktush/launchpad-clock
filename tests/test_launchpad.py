from launchpad_clock.launchpad import AMBER, OFF, Launchpad


class FakeOut:
    def __init__(self):
        self.sent = []

    def send(self, m):
        self.sent.append(m)


def pad():
    p = Launchpad()
    p.out = FakeOut()
    return p


def test_only_changes_are_sent():
    p = pad()
    p.set_pad(0, 0, AMBER)
    p.set_pad(0, 0, AMBER)
    p.set_pad(1, 0, OFF)
    assert len(p.out.sent) == 1


def test_invalidate_resends_everything_including_off():
    p = pad()
    p.set_pad(0, 0, AMBER)
    p.invalidate()
    p.set_pad(0, 0, AMBER)
    p.set_pad(1, 0, OFF)
    assert len(p.out.sent) == 3
