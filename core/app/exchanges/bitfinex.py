# -*- coding: utf-8 -*-
import time
import requests
import logging


from app.exchanges.helpers import insert_candles
from app.utils.influx_utils import check_last_timestamp
from .base import BaseExchange


class Bitfinex(BaseExchange):
    timeframes = ['1h', '3h', '6h', '12h', '24h']
    name = 'Bitfinex'

    def json(self, measurement: str, row: list) -> dict:
        json_body = {
            "measurement": measurement,
            "tags": {'exchange': self.name.lower()},
            "time": int(row[0]),
            "fields": {
                "open": float(row[1]),
                "close": float(row[2]),
                "high": float(row[3]),
                "low": float(row[4]),
                "volume": float(row[5]),
            }
        }
        return json_body

    def fetch_candles(self, pair: str, timeframe: str) -> bool:
        measurement = pair + timeframe

        timeframeR = timeframe
        if timeframe == '24h':
            timeframeR = '1D'

        start = (check_last_timestamp(measurement)) * 1000   # ms
        end = (int(time.time()) + 100) * 1000  # ms

        url = f'https://api-pub.bitfinex.com/v2/candles/trade:{timeframeR}:t{pair}/hist'
        params = {
            'start': start,
            'end': end,
            'limit': 5000
        }

        request = requests.get(url, params=params)
        response = request.json()

        # Check if response was successful
        if request.status_code != 200:
            logging.info(f'No success {response}')
            return False

        if not isinstance(response, list):
            logging.info('Bitfinex response is not a list.')
            return False

        if (response and response[0] == 'error') or (not response):
            logging.info(f'Bitfinex response failed: {response}')
            return False

        # Make candles
        points = [self.json(measurement, row) for row in response]

        result = insert_candles(points, measurement, self.name, time_precision="ms")

        return result
