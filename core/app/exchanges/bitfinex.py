# -*- coding: utf-8 -*-
import time

import requests

from app.models.influx import check_last_timestamp

from .base import BaseExchange


class Bitfinex(BaseExchange):
    timeframes = ["1h", "3h", "6h", "12h", "24h"]
    name = "Bitfinex"
    time_precision = "ms"

    def json(self, measurement: str, row: list) -> dict:
        json_body = {
            "measurement": measurement,
            "tags": {"exchange": self.name.lower()},
            "time": int(row[0]),
            "fields": {
                "open": float(row[1]),
                "close": float(row[2]),
                "high": float(row[3]),
                "low": float(row[4]),
                "volume": float(row[5]),
            },
        }
        return json_body

    def fetch_candles(self, timeframe: str) -> bool:
        measurement = self.pair + timeframe
        start = (check_last_timestamp(measurement)) * 1000  # ms
        end = (int(time.time()) + 100) * 1000  # ms

        btimeframe = "1D" if timeframe == "24h" else timeframe
        url = f"https://api-pub.bitfinex.com/v2/candles/trade:{btimeframe}:t{self.pair}/hist"
        params = {"start": start, "end": end, "limit": 5000}

        response = requests.get(url, params=params)
        body = response.json()

        # Check if response was successful
        success = (
            response.status_code == 200
            and body
            and isinstance(body, list)
            and body[0] != "error"
        )
        if not success:
            self.log_error(response)
            return False

        # Make candles
        points = [self.json(measurement, row) for row in body]

        return self.insert_candles(points, measurement)
