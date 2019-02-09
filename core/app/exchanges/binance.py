# -*- coding: utf-8 -*-
import time
import traceback
import requests
import logging
from datetime import datetime as dt
from app.exchanges.helpers import insert_candles


class Binance():
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

    def get_candles(self, pair, timeframe):
        mesurement = pair + timeframe
        pair_formated = self.pair_format(pair)

        # Map timeframes for Binance
        timeframeR = timeframe
        if timeframe == '24h':
            timeframeR = '1d'
        elif timeframe == '168h':
            timeframeR = '1w'

        # start = helper.check_last_tmstmp(self.influx, pair, timeframe)
        # end = int(time.time()) + 100

        # max last 500 candles
        url = f'https://api.binance.com/api/v1/klines?symbol={pair_formated}&interval={timeframeR}&limit=500'
        request = requests.get(url)
        response = request.json()


        if not isinstance(response, list):
            logging.error('FAILED {} Binance response: {}'.format(mesurement, response.get('msg', 'no error')))
            return False

        # Make candles
        points = []
        for row in response:
            json_body = {
                "measurement": mesurement,
                "time": int(1000 * row[0]),
                "fields": {
                    "open": float(row[1]),
                    "close": float(row[4]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "volume": float(row[5]),
                }
            }
            points.append(json_body)

        result = insert_candles(self.influx, points, mesurement)

        if timeframe == '1h':
            self.downsample_3h(pair)

        return result

    def fill(self, pair):
        for tf in  ['1h', '2h', '6h', '12h', '24h']:
            status = self.get_candles(pair, tf)
            if not status:
                logging.error(f'Failed to fill {pair}:{tf}')
            time.sleep(2)
        return status
