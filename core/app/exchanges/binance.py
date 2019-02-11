# -*- coding: utf-8 -*-
import time
import traceback
import requests
import logging
from datetime import datetime as dt
from app.exchanges.helpers import insert_candles


class Binance:
    def __init__(self, influx_client):
        self.influx = influx_client
        self.name = 'Binance'

    def pair_format(self, pair):
        end_pair = pair[-3:]
        start_pair = pair[:-3]
        if end_pair == 'USD':
            end_pair = end_pair + 'T'
        return start_pair + end_pair

    def downsample_3h(self, pair):
        time_now = dt.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            query = f"""
                        SELECT 
                        first(open) AS open, 
                        max(high) AS high, 
                        min(low) AS low, 
                        last(close) AS close, 
                        sum(volume) AS volume 
                        INTO {pair}3h FROM {pair}1h WHERE time <= '{time_now}' GROUP BY time(3h)

                """
            self.influx.query(query)
        except:
            logging.error(f'FAILED 3h downsample {pair} error: \n {traceback.format_exc()}')
            pass

    def fetch_candles(self, pair, timeframe):
        measurement = pair + timeframe
        pair_formated = self.pair_format(pair)

        # Map timeframes for Binance
        timeframeR = timeframe
        if timeframe == '24h':
            timeframeR = '1d'
        elif timeframe == '168h':
            timeframeR = '1w'

        # max last 500 candles
        url = f'https://api.binance.com/api/v1/klines?symbol={pair_formated}&interval={timeframeR}&limit=500'
        request = requests.get(url)
        response = request.json()


        if not isinstance(response, list) or request.status_code != 200:
            logging.error(f"FAILED {measurement} Binance response: {response.get('msg', 'no error')}")
            return False

        # Make candles
        points = []
        for row in response:
            json_body = {
                "measurement": measurement,
                "time": int(row[0]),
                "fields": {
                    "open": float(row[1]),
                    "close": float(row[4]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "volume": float(row[5]),
                }
            }
            points.append(json_body)

        result = insert_candles(self.influx, points, measurement, time_precision='ms')

        if timeframe == '1h':
            self.downsample_3h(pair)

        return result

    def check(self, pair):
        # max last 500 candles
        pair_formated = self.pair_format(pair)
        url = f'https://api.binance.com/api/v1/klines?symbol={pair_formated}&interval=1d&limit=500'
        request = requests.get(url)
        response = request.json()

        if not isinstance(response, list):
            logging.error(f"FAILED Binance response: {response.get('msg', 'no error')}")
            return self.name.lower(), 0

        return self.name.lower(), len(response)


    def fill(self, pair):
        for tf in  ['1h', '2h', '6h', '12h', '24h']:
            status = self.fetch_candles(pair, tf)
            if not status:
                logging.error(f'Failed to fill {pair}:{tf}')
            time.sleep(2)
        return status
