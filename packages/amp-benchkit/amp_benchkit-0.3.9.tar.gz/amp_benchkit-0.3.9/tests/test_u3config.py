import math

import amp_benchkit.u3config as u3cfg


class DummyU3:
    def __init__(self, calls):
        self.calls = calls
        self.closed = False

    def getAIN(self, ch, **kwargs):
        self.calls.append((ch, kwargs))
        # Deterministic value that depends on channel (scaled for readability)
        return ch + 0.5

    def close(self):
        self.closed = True


def test_u3_read_ain_extended_range(monkeypatch):
    calls = []
    dev = DummyU3(calls)
    monkeypatch.setattr(u3cfg, "u3_open", lambda: dev)

    val = u3cfg.u3_read_ain(14, resolution_index=5)
    assert math.isclose(val, 14.5)
    # Resolution index is clamped/passed through
    assert calls == [(14, {"ResolutionIndex": 5})]
    assert dev.closed


def test_u3_read_ain_resolution_clamp(monkeypatch):
    calls = []
    dev = DummyU3(calls)
    monkeypatch.setattr(u3cfg, "u3_open", lambda: dev)

    u3cfg.u3_read_ain(3, resolution_index=99)
    # Clamp to max 12
    assert calls[-1] == (3, {"ResolutionIndex": 12})


def test_u3_read_ain_legacy_resolution_fallback(monkeypatch):
    class LegacyDummy(DummyU3):
        def __init__(self, calls):
            super().__init__(calls)
            self.kw_errors = []

        def getAIN(self, ch, **kwargs):
            if kwargs:
                self.kw_errors.append((ch, kwargs))
                raise TypeError("getAIN() got an unexpected keyword argument 'ResolutionIndex'")
            return super().getAIN(ch, **kwargs)

    calls = []
    dev = LegacyDummy(calls)
    monkeypatch.setattr(u3cfg, "u3_open", lambda: dev)

    val = u3cfg.u3_read_ain(2, resolution_index=4)
    assert math.isclose(val, 2.5)
    # First attempt should record kw failure, final call logs fallback
    assert dev.kw_errors == [(2, {"ResolutionIndex": 4})]
    assert calls == [(2, {})]


def test_u3_read_multi_filters_channels(monkeypatch):
    calls = []

    class MultiDummy(DummyU3):
        def getAIN(self, ch, **kwargs):
            self.calls.append((ch, kwargs))
            return ch * 0.1

    dev = MultiDummy(calls)
    monkeypatch.setattr(u3cfg, "u3_open", lambda: dev)

    rows = u3cfg.u3_read_multi([-1, 0, 3, 99], samples=2, resolution_index=11)
    assert rows == [[0.0, 0.30000000000000004], [0.0, 0.30000000000000004]]
    expected = [
        (0, {"ResolutionIndex": 11}),
        (3, {"ResolutionIndex": 11}),
        (0, {"ResolutionIndex": 11}),
        (3, {"ResolutionIndex": 11}),
    ]
    assert calls == expected
    assert dev.closed


def test_u3_read_multi_defaults_to_channel_zero(monkeypatch):
    calls = []
    dev = DummyU3(calls)
    monkeypatch.setattr(u3cfg, "u3_open", lambda: dev)

    rows = u3cfg.u3_read_multi([], samples=1)
    assert rows == [[0.5]]
    assert calls == [(0, {})]


def test_u3_read_multi_legacy_resolution_fallback(monkeypatch):
    class LegacyDummy(DummyU3):
        def __init__(self, calls):
            super().__init__(calls)
            self.kw_errors = []

        def getAIN(self, ch, **kwargs):
            if kwargs:
                self.kw_errors.append((ch, kwargs))
                raise TypeError("getAIN() got an unexpected keyword argument 'ResolutionIndex'")
            return super().getAIN(ch, **kwargs)

    calls = []
    dev = LegacyDummy(calls)
    monkeypatch.setattr(u3cfg, "u3_open", lambda: dev)

    rows = u3cfg.u3_read_multi([0, 1], samples=1, resolution_index=3)
    assert rows == [[0.5, 1.5]]
    assert dev.kw_errors == [(0, {"ResolutionIndex": 3})]
    assert calls == [(0, {}), (1, {})]
