from app.ta.patterns.double import make_double
from app.ta.levels import Levels
import numpy as np

class TestTA:
    def test_make_double_top(self):
        a = np.arange(0, 40)
        b = np.arange(30, 40)
        c = np.concatenate([a, b[::-1], b, a[::-1]])

        d = make_double(np.arange(c.size), c, type_='top')

        # assert structure
        assert isinstance(d, dict)
        assert 'info' in d.keys() and isinstance(d['info'], list)
        for k in ['A', 'B', 'C']:
            assert k in d.keys()
            assert isinstance(d[k], tuple)

        x, y = d['A']
        assert x == 39
        assert y == 39


    def test_make_double_bottom(self):
        a = np.arange(0, 40)
        b = np.arange(0, 5)
        c = np.concatenate([a[::-1], b, b[::-1], a])

        d = make_double(np.arange(c.size), c, type_='bottom')
        assert isinstance(d, dict)
        assert 'info' in d.keys() and isinstance(d['info'], list)
        for k in ['A', 'B', 'C']:
            assert k in d.keys()
            assert isinstance(d[k], tuple)

        x, y = d['A']
        assert x == 39
        assert y == 0

    def test_levels(self):
        a = np.arange(50, 101, 5)
        b = np.arange(0, 100, 5)[::-1]
        c = np.arange(0, 70, 5)
        d = np.arange(0, 70, 5)[::-1]
        e = np.arange(0, 30, 5)
        close = np.concatenate([a, b, c, d, e])

        lvl = Levels('test','test', close, np.arange(close.size))
        lvl.start = 0

        d = lvl.make()
        print(d)

        assert isinstance(d, dict)
        for k in ['fib', 'support', 'resistance', 'info']:
            assert k in d.keys()
            assert isinstance(d[k], list)
            # assert False

        assert d['resistance'] == [100, 65]
        assert d['support'] == [0]
        assert d['fib'] == [0.0, 23.599999999999998, 38.2, 50.0, 61.8, 100.0]