import numpy as np
import random
import string

from app.ta.levels import Levels
from app.database.models import Level
from app.ta.charting.base import Universe


class TestLevels:
    a = np.arange(50, 101, 2)
    b = np.arange(0, 100, 2)[::-1]
    c = np.arange(0, 70, 2)
    d = np.arange(0, 70, 2)[::-1]
    e = np.arange(0, 30, 2)
    close = np.concatenate([a, b, c, d, e])

    @staticmethod
    def _time(close: np.ndarray) -> np.ndarray:
        return np.arange(close.size)

    def _levels(self, close, app):
        universe = Universe(
            pair="".join(random.choice(string.ascii_letters) for _ in range(12)),
            timeframe="test_tf",
            close=close,
            time=self._time(close),
            future_time=np.array([]),
        )
        lvl = Levels(universe)
        with app.ctx:
            result = lvl()["levels"]
        return result, universe.pair, universe.timeframe

    def test_structure(self, app):
        close = np.concatenate([self.a, self.b])
        result, pair, tf = self._levels(close, app)

        assert isinstance(result, dict)
        assert "info" in result.keys()
        assert "levels" in result.keys()

        assert isinstance(result["levels"], list)

    def test_level_info(self, app):
        close = np.concatenate([self.a, self.b])
        result, pair, tf = self._levels(close, app)

        levels = result["levels"]
        assert len(levels) == 1

        level = levels[0]
        assert isinstance(level, dict)

        keys = level.keys()
        for k in [
            "type",
            "tf",
            "value",
            "resistance",
            "support",
            "strength",
            "first_occurrence",
        ]:
            assert k in keys

        # Check if level was found correctly
        assert level["type"] == "resistance"
        assert level["value"] == 100
        assert level["tf"] == tf
        assert level["resistance"] == 1
        assert level["support"] == 0
        assert level["strength"] == 2

        # Check if level was saved to database
        with app.ctx:
            result = Level.query.filter_by(pair=pair).all()

        assert len(result) == 1
        level = result[0]
        assert level.type == "resistance"
        assert level.value == 100
        assert level.strength == 2

    def test_two_levels(self, app):
        close = np.concatenate([self.a, self.b, self.c])
        result, pair, tf = self._levels(close, app)

        assert len(result["levels"]) == 2
        result["levels"].sort(key=lambda x: x["type"])

        resistance, support = result["levels"]

        assert resistance["type"] == "resistance"
        assert support["type"] == "support"

        assert resistance["value"] == 100
        assert support["value"] == 0
