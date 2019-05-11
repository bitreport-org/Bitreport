import numpy as np
import random
import string

from app.ta.levels import Levels
from app.api.database import Level


class TestLevels:
    a = np.arange(50, 101, 2)
    b = np.arange(0, 100, 2)[::-1]
    c = np.arange(0, 70, 2)
    d = np.arange(0, 70, 2)[::-1]
    e = np.arange(0, 30, 2)
    close = np.concatenate([a, b, c, d, e])
    time = np.arange(close.size)

    def _levels(self, close, app):
        pair =''.join(random.choice(string.ascii_letters) for _ in range(12))
        tf = 'test_tf'
        lvl = Levels(pair, tf, close, self.time)
        with app.ctx:
            result = lvl()
        return result, pair, tf

    def test_structure(self, app):
        close = np.concatenate([self.a, self.b])
        result, pair, tf = self._levels(close, app)

        assert isinstance(result, dict)
        assert 'info' in result.keys()
        assert 'levels' in result.keys()

        assert isinstance(result['levels'], list)

    def test_level_info(self, app):
        close = np.concatenate([self.a, self.b])
        result, pair, tf = self._levels(close, app)

        levels = result['levels']
        assert len(levels) == 1

        level = levels[0]
        assert isinstance(level, dict)

        keys = level.keys()
        for k in ['type', 'tf', 'value', 'resistance', 'support', 'strength', 'first_occurrence']:
            assert k in keys

        # Check if level was found correctly
        assert level['type'] == 'resistance'
        assert level['value'] == 100
        assert level['tf'] == tf
        assert level['resistance'] == 1
        assert level['support'] == 0
        assert level['strength'] == 1

        # Check if level was saved to database
        with app.ctx:
            result = Level.query.filter_by(pair=pair).all()

        assert len(result) == 1
        level = result[0]
        assert level.type == 'resistance'
        assert level.value == 100
        assert level.strength == 1


    def test_two_levels(self, app):
        close = np.concatenate([self.a, self.b, self.c])
        result, pair, tf = self._levels(close, app)

        assert len(result['levels']) == 2
        result['levels'].sort(key=lambda x: x['type'])

        resistance, support = result['levels']

        assert resistance['type'] == 'resistance'
        assert support['type'] == 'support'

        assert resistance['value'] == 100
        assert support['value'] == 0
