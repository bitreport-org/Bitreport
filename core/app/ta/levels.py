import numpy as np
from collections import namedtuple
from functools import reduce
from app.api.database import Level
from app.api import db


LevelTuple = namedtuple('LevelTuple', ['type', 'value', 'strength'])


class FuzzyLevel:
    def __init__(self, lvl: Level, last_price: float, eps: float=0.005) -> None:
        self.lvl = lvl
        self.lower = lvl.value * (1 - eps)
        self.upper = lvl.value * (1 + eps)
        self.resistance = 0
        self.support = 0
        self.eps = eps
        self.dist = lvl.value - last_price

    def __repr__(self):
        return f'{self.lvl.type.upper()} {self.lvl.value} {self.lvl.strength}' \
               f'R: {self.resistance} S: {self.support}'

    def __eq__(self, other):
        val1 = self.lower <= other.lvl.value <= self.upper
        val2 = other.lower <= self.lvl.value <= other.upper
        return val1 or val2

    def json(self) -> dict:
        return {'resistance': self.resistance,
                'support': self.support,
                'value': self.lvl.value,
                'strength': self.lvl.strength,
                'type': self.lvl.type,
                'tf': self.lvl.timeframe}

    @property
    def score(self) -> int:
        return self.support + self.resistance

    def update(self, others: list):
        for other in others:
            if self == other:
                if other.lvl.type == 'resistance':
                    self.resistance += 1
                else:
                    self.support += 1
        return self


class Levels(object):
    _radius_map = {
        4: 60,
        3: 30,
        2: 20,
        1: 10
    }

    def __init__(self, pair: str, timeframe: str, close: np.ndarray) -> None:
        self.pair = pair
        self.timeframe = timeframe
        self.close = close

    def _save_levels(self, levels: list) -> None:
        for x in levels:
            params = dict(
                pair=self.pair,
                timeframe=self.timeframe,
                strength=x.strength,
                type=x.type,
                value=float(x.value)
            )
            lvl = Level.query.filter_by(**params).first()
            if not lvl:
                db.session.add(Level(**params))

        db.session.commit()

    def _check(self, i: int, x: float, xs: np.ndarray) -> tuple:
        """
        Checks if value x is a significant level in series of xs.
        Parameters
        ----------
        i - index of x in xs
        x - price value
        xs - array of price values

        Returns
        -------
        (type, value, strength) or None if x is not a level
        """
        lvl = None

        # For each strength level
        for strength, radius in self._radius_map.items():
            if i > xs.size - radius:
                continue
            if i < radius:
                continue
            ys = xs[i - radius : i + radius]
            support = reduce(lambda a, b: a and b, ys >= np.array([x] * ys.size))
            resistance = reduce(lambda a, b: a and b, ys <= np.array([x] * ys.size))
            if support:
                lvl = LevelTuple('support', x, strength)
            elif resistance:
                lvl = LevelTuple('resistance', x, strength)

        return lvl

    def find_levels(self, close: np.ndarray) -> None:
        lvls = [self._check(i, x, close) for i, x in enumerate(close)]
        lvls = list(filter(lambda x: x, lvls))
        self._save_levels(lvls)

    @staticmethod
    def _fib_levels(close: np.ndarray, top: float, bottom: float) -> list:
        top_index = np.where(close == top)[0][-1]
        bottom_index = np.where(close == bottom)[0][-1]

        height = top - bottom
        fib_lvls = (0.00, .236, .382, .500, .618, 1.00)

        if top_index < bottom_index:
            levels = map(lambda x: bottom + x * height, fib_lvls)
        else:
            levels = map(lambda x: bottom - x * height, fib_lvls)

        return list(levels)

    def _score_levels(self, close: np.ndarray, r: float = 0.03) -> list:
        """
        Looks for levels in the given range (r% margin). Then, each
        level is converted to fuzzy level. Next we find number of
        neighbors of each level. Finally we select best support and
        resistance.

        Parameters
        ----------
        close: price values
        r - float from (0,1), additional margin for level search

        Returns
        -------
        list
        """
        # Take levels between prices
        price_max = float(np.max(close))
        price_min = float(np.min(close))

        lvls = Level.query. \
            filter_by(pair=self.pair). \
            filter(Level.value >= (1 - r) * price_min). \
            filter(Level.value <= (1 + r) * price_max). \
            order_by(Level.value).distinct(Level.value, Level.type).all()

        # Crate FuzzyLevels
        last_price = close[-1]
        lvls = [FuzzyLevel(lvl, last_price) for lvl in lvls]
        lvls = [lvl.update(lvls) for lvl in lvls]

        resistance = list(filter(lambda x: x.dist > 0, lvls))
        support = list(filter(lambda x: x.dist < 0, lvls))

        output = []
        # TODO: what if same score but different strength?
        if resistance:
            resistance.sort(key=lambda x: x.score)
            output.append(resistance[-1])

        if support:
            support.sort(key=lambda x: x.score)
            output.append(support[-1])

        return list(map(lambda x: x.json(), output))


    def make(self) -> dict:
        # TODO: do not create levels with each request...
        # Look for new  new levels
        self.find_levels(self.close)

        # Select best levels
        levels = {
            'levels': self._score_levels(self.close),
            'info': []
        }
        return levels
