# -*- coding: utf-8 -*-
import requests

from .base import BaseExchange


class Binance(BaseExchange):
    timeframes = ["1h", "2h", "6h", "12h", "24h"]
    name = "Binance"
    pool = 5
    time_precision = "ms"

    @staticmethod
    def _pair_format(pair: str) -> str:
        end_pair = pair[-3:]
        start_pair = pair[:-3]
        if end_pair == "USD":
            end_pair = end_pair + "T"
        return start_pair + end_pair

    def json(self, measurement: str, row: list) -> dict:
        json_body = {
            "measurement": measurement,
            "tags": {"exchange": self.name.lower()},
            "time": int(row[0]),
            "fields": {
                "open": float(row[1]),
                "close": float(row[4]),
                "high": float(row[2]),
                "low": float(row[3]),
                "volume": float(row[5]),
            },
        }
        return json_body

    def fetch_candles(self, timeframe: str, limit: int = 500) -> bool:
        measurement = self.pair + timeframe
        pair_formated = self._pair_format(self.pair)

        # Map timeframes for Binance
        mapped_tf = "1d" if timeframe == "24h" else timeframe
        mapped_tf = "12" if mapped_tf == "168h" else mapped_tf

        # max last 500 candles
        url = f"https://api.binance.com/api/v1/klines"
        params = {"symbol": pair_formated, "interval": mapped_tf, "limit": limit}

        response = requests.get(url, params=params)
        body = response.json()

        if not isinstance(body, list) or response.status_code != 200:
            self.log_error(response)
            return False

        # Make candles
        points = [self.json(measurement, row) for row in body]
        return self.insert_candles(points, measurement)
