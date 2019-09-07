import logging
from typing import Tuple

import numpy as np

import config
from app.models import Series
from app.models.influx import check_last_timestamp, get_candles
from app.ta.events.triangle import simple_wedge
from app.ta.indicators import make_indicators


class PairData:
    def __init__(
        self, pair: str, timeframe: str, limit: int, last_timestamp: int
    ) -> None:
        """
        To return data without NaN values indicators are calculated on period of
        length: limit + magic_limit, however data returned by prepare() has length = limit
        """
        self.magic_limit = config.BaseConfig.MAGIC_LIMIT
        self.margin = config.BaseConfig.MARGIN

        self.pair = pair
        self.timeframe = timeframe
        self.limit = max(limit, 20)
        self.last_timestamp = last_timestamp

        self.dates = []
        self.data = Series(self.pair, self.timeframe)
        self.output = dict()

    def prepare(self) -> Tuple[dict, int]:
        """
        Selects price data from influx database, adds technical indicators and some other magic

        Returns
        -------
        (response, code)
        """
        # Data request
        self.data: Series = get_candles(
            pair=self.pair,
            timeframe=self.timeframe,
            limit=self.limit + self.magic_limit,
            last_timestamp=self.last_timestamp,
        )

        # Handle empty measurement
        if not np.any(self.data.date):
            message = dict(msg=f"No data for {self.pair+self.timeframe}", last=None)
            logging.error(message)
            return message, 204

        # Price data and information
        price = {
            k: getattr(self.data, k).tolist()[-self.limit :]
            for k in ["open", "high", "close", "low"]
        }

        price.update(info=[])

        # Volume data and information
        volume = dict(volume=self.data.volume.tolist()[-self.limit :], info=[])

        # Prepare dates
        last = self._last_filling()

        dates = generate_dates(self.data.date, self.timeframe, self.margin)
        self.dates = dates[-(self.limit + self.margin) :]

        indicators_dict = self._make_indicators()

        indicators_dict.update(price=price)
        indicators_dict.update(volume=volume)

        response = dict(dates=self.dates, indicators=indicators_dict, last=last)
        return response, 200

    def _last_filling(self):
        last = check_last_timestamp(f"{self.pair.upper()}1h", minus=0)
        return last

    def _make_indicators(self) -> dict:
        indicators_values = dict()

        # Indicators
        indicators_values.update(make_indicators(self.data, self.limit))

        indicators_values.update(simple_wedge(series=self.data))

        # Wedges
        # wg = charting.Charting(universe)
        # indicators_values.update(wg())

        # Patterns
        # indicators_values.update(patterns.double_top(universe))
        # indicators_values.update(patterns.double_bottom(universe))

        # Levels
        # lvl = Levels(universe)
        # indicators_values.update(lvl())

        return indicators_values


def generate_dates(date: list, timeframe: str, n: int) -> list:
    """
    Generates next n timestamps in interval of a given timeframe
    """
    _map = {"m": 60, "h": 3600, "W": 648000}
    dt = _map[timeframe[-1]] * int(timeframe[:-1])
    if isinstance(date, np.ndarray):
        date = date.tolist()

    date = date + [date[-1] + (i + 1) * dt for i, x in enumerate(range(n))]

    return date
