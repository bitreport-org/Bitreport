# -*- coding: utf-8 -*-
import requests
import logging

from app.exchanges.helpers import insert_candles
from .base import BaseExchange


class Bittrex(BaseExchange):
    timeframes = ['1h', '24h']
    name = 'Bittrex'
    pool = 2

    @staticmethod
    def _pair_format(pair: str) -> str:
        end_pair = pair[-3:]
        start_pair = pair[:-3]
        if end_pair == 'USD':
            end_pair = end_pair + 'T'
        return end_pair + '-' + start_pair

    def json(self, measurement: str, row: dict) -> dict:
        json_body = {
            "measurement": measurement,
            "tags": {'exchange': self.name.lower()},
            "time": row['T'],
            "fields": {
                "open": float(row['O']),
                "close": float(row['C']),
                "high": float(row['H']),
                "low": float(row['L']),
                "volume": float(row['BV']),
            }
        }
        return json_body

    def fetch_candles(self, pair, timeframe: str, limit: int = 0) -> bool:
        result = False
        measurement = pair + timeframe
        pair_formated = self._pair_format(pair)

        timeframes = {'1h': 'hour', '24h': 'day'}
        btf = timeframes.get(timeframe, '1h')

        url = f'https://international.bittrex.com/Api/v2.0/pub/market/GetTicks'
        params = {
            'marketName': pair_formated,
            'tickInterval': btf
        }

        request = requests.get(url, params=params)
        response = request.json()

        # Check if response was successful
        if 'success' not in response.keys() or request.status_code != 200:
            logging.info(f"FAILED {measurement} Bitrex response: {response.get('message','no message')}")
            return False

        rows = response.get('result', False)

        if not rows:
            logging.info(f"FAILED {measurement} Bitrex empty response")
            return False

        points = [self.json(measurement, row) for row in rows[-limit:]]

        result = insert_candles(points, measurement, self.name, time_precision="s")

        return result
