# -*- coding: utf-8 -*-
import requests
import logging
from app.exchanges.helpers import insert_candles, downsample


class Bittrex:
    def __init__(self, influx_client):
        self.influx = influx_client
        self.name = 'Bittrex'

    @staticmethod
    def _pair_format(pair):
        end_pair = pair[-3:]
        start_pair = pair[:-3]
        if end_pair == 'USD':
            end_pair = end_pair + 'T'
        return end_pair + '-' + start_pair

    def _downsample(self, pair, from_tf, to_tf):
        downsample(self.influx, pair=pair, from_tf=from_tf, to_tf=to_tf)

    def fetch_candles(self, pair, timeframe):
        result = False
        measurement = pair + timeframe
        pair_formated = self._pair_format(pair)

        timeframes = {'1h': 'hour', '24h': 'day'}
        btf = timeframes.get(timeframe, '1h')

        url = f'https://bittrex.com/Api/v2.0/pub/market/GetTicks'
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
        if rows:
            points = []
            for row in rows:
                json_body = {
                    "measurement": measurement,
                    "tags": {'exchange' : self.name.lower()},
                    "time": row['T'],
                    "fields": {
                        "open": float(row['O']),
                        "close": float(row['C']),
                        "high": float(row['H']),
                        "low": float(row['L']),
                        "volume": float(row['BV']),
                    }
                }
                points.append(json_body)
            result = insert_candles(self.influx, points, measurement, self.name, time_precision="s")
            if timeframe == '1h':
                for tf in ['2h', '3h', '6h', '12h']:
                    self._downsample(pair, '1h', tf)

        return result

    def fill(self, pair):
        for tf in ['1h', '24h']:
            status = self.fetch_candles(pair, tf)
            if not status:
                return False
        return status
