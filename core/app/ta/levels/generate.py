from influxdb import InfluxDBClient
from flask import Flask
import logging
import numpy as np

from app.utils.helpers import get_candles
from .levels import Levels
from app.ta.charting.base import Universe


def generate_levels(app: Flask,
                    influx: InfluxDBClient,
                    pair: str,
                    limit: int = 500) -> None:

    logged = False
    for tf in ['1h', '2h', '3h', '6h', '12h', '24h']:
        data = get_candles(influx, pair, tf, limit)
        close = data.get('close')
        date = np.array(data.get('date'))

        if close.size < 1 and date.size < 1:
            continue

        universe = Universe(
            pair=pair,
            timeframe=tf,
            close=close,
            time=date[:close.size],
            future_time=[]
        )

        # Find levels and save them
        try:
            with app.app_context():
                Levels(universe)()
        except (ValueError, AssertionError):
            if not logged:
                logging.error(f'Levels production unsuccessful for {pair} and {tf}')
                logged = True
            pass
