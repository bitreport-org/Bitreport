import numpy as np

import app.ta.constructors as cts


class TestConstructors:
    a = np.arange(50, 101, 2)
    b = np.arange(0, 100, 2)[::-1]
    c = np.arange(1, 70, 2)
    d = np.arange(0, 69, 2)[::-1]
    e = np.arange(1, 30, 2)
    close = np.concatenate([a, b, c, d, e])
    time = np.arange(close.size)

    # peaks
    A = cts.Point(25, 100)
    B = cts.Point(75, 0)
    C = cts.Point(110, 69)
    D = cts.Point(145, 0)

    def test_tops(self):
        tops = cts.tops(self.close, self.time)
        assert isinstance(tops, list)
        assert len(tops) == 2

        a, b = tops
        assert isinstance(a, cts.Point)
        assert isinstance(b, cts.Point)

        assert a == self.A
        assert b == self.C

    def test_bottoms(self):
        bottoms = cts.bottoms(self.close, self.time)
        assert isinstance(bottoms, list)
        assert len(bottoms) == 2

        a, b = bottoms
        assert isinstance(a, cts.Point)
        assert isinstance(b, cts.Point)

        assert a == self.B
        assert b == self.D

    def test_hline_up(self):
        lines = cts.hline_up(self.close, self.time)
        assert isinstance(lines, list)
        assert len(lines) == 2

    def test_hline_down(self):
        lines = cts.hline_down(self.close, self.time)
        assert isinstance(lines, list)
        assert len(lines) == 2

    def test_skew(self):
        a = cts.Point(0.0, 0.0)
        b = cts.Point(10.0, 0.0)

        skew = cts._skew(a, b)
        assert skew.coef == 0.0
        assert skew.slope == 0.0

    def test_up_skews(self):
        skews = cts.skews_up(self.close, self.time)

        assert isinstance(skews, list)
        assert len(skews) == 1

        assert cts._skew(self.A, self.C) == skews[0]

    def test_down_skews(self):
        skews = cts.skews_down(self.close, self.time)

        assert isinstance(skews, list)
        assert len(skews) == 1

        assert cts._skew(self.B, self.D) == skews[0]
