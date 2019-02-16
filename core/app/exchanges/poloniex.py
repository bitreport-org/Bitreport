# -*- coding: utf-8 -*-
import time
import traceback
import requests
import logging
from datetime import datetime as dt
from app.exchanges.helpers import insert_candles, check_last_tmstmp


class Poloniex:
    def __init__(self, influx_client):
        self.influx = influx_client
        self.name = 'Poloniex'

    def pair_format(self, pair):
        end_pair = pair[-3:]
        start_pair = pair[:-3]
        if end_pair == 'USD':
            end_pair = end_pair + 'T'
        return end_pair + '_' + start_pair

    def downsample(self, pair, from_tf, to_tf):
        time_now = dt.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            query = f"""
                        SELECT 
                        first(open) AS open, 
                        max(high) AS high, 
                        min(low) AS low, 
                        last(close) AS close, 
                        sum(volume) AS volume 
                        INTO {pair+to_tf} FROM {pair+from_tf} WHERE time <= '{time_now}' GROUP BY time({to_tf}), *

                """
            self.influx.query(query)
        except:
            logging.error(f'FAILED {to_tf} downsample {pair} error: \n {traceback.format_exc()}')
            pass

    def fetch_candles(self, pair, timeframe):
        measurement = pair + timeframe
        pair_formated = self.pair_format(pair)

        start = check_last_tmstmp(self.influx, measurement)

        # Here we map our possible timeframes 1h, 2h, 3h, 6h, 12h to
        # format acceptable by Poloniex API
        tf_map = {'30m': 1800, '2h': 7200, '24h': 86400}
        if timeframe not in tf_map.keys():
            if timeframe in ['1h', '3h']:
                timeframe='30m'
            else:
                timeframe = '2h'
        measurement = pair + timeframe

        url = f'https://poloniex.com/public?command=returnChartData&currencyPair={pair_formated}&start={start-30}&period={tf_map[timeframe]}'
        request = requests.get(url)
        response = request.json()

        # Check if response was successful
        if request.status_code != 200 or not isinstance(response, list):
            logging.error(f"FAILED {measurement} Poloniex response: {response}")
            return False

        points = []
        for row in response:
            json_body = {
                "measurement": measurement,
                "tags": {'exchange' : self.name.lower()},
                "time": int(row['date']),
                "fields": {
                    "open": float(row['open']),
                    "close": float(row['close']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "volume": float(row['volume']),
                }
            }
            points.append(json_body)

        result = insert_candles(self.influx, points, measurement, self.name, time_precision='s')

        if timeframe == '30m':
            for tf in ['1h', '3h']:
                self.downsample(pair, '30m', tf)

        if timeframe == '2h':
            for tf in ['6h', '12h']:
                self.downsample(pair, '2h', tf)

        return result

    def fill(self, pair):
        for tf in ['30m', '2h', '24h']:
            status = self.fetch_candles(pair, tf)
            if not status:
                return False
        return status
