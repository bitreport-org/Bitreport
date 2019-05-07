import numpy as np

from app.ta.patterns.double import make_double


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
