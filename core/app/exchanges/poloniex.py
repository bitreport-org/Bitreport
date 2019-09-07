# -*- coding: utf-8 -*-
import requests

from app.models.influx import check_last_timestamp

from .base import BaseExchange


class Poloniex(BaseExchange):
    timeframes = ["30m", "2h", "24h"]
    name = "Poloniex"
    pool = 3
    time_precision = "s"

    @staticmethod
    def _pair_format(pair: str) -> str:
        end_pair = pair[-3:]
        start_pair = pair[:-3]
        if end_pair == "USD":
            end_pair = end_pair + "T"
        return end_pair + "_" + start_pair

    def json(self, measurement: str, row: dict) -> dict:
        json_body = {
            "measurement": measurement,
            "tags": {"exchange": self.name.lower()},
            "time": int(row["date"]),
            "fields": {
                "open": float(row["open"]),
                "close": float(row["close"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "volume": float(row["volume"]),
            },
        }
        return json_body

    def fetch_candles(self, timeframe: str) -> bool:
        # Here we map our possible timeframes 1h, 2h, 3h, 6h, 12h to
        # format acceptable by Poloniex API
        tf_map = {"30m": 1800, "2h": 7200, "24h": 86400}

        if timeframe not in tf_map.keys():
            timeframe = "30m" if timeframe in ["1h", "3h"] else "2h"

        measurement = self.pair + timeframe

        start = check_last_timestamp(measurement)
        params = {
            "command": "returnChartData",
            "currencyPair": self._pair_format(self.pair),
            "start": start - 30,
            "period": tf_map[timeframe],
        }

        url = f"https://poloniex.com/public"
        response = requests.get(url, params=params)
        body = response.json()

        # Check if response was successful
        if response.status_code != 200 or not isinstance(body, list):
            self.log_error(response)
            return False

        points = [self.json(measurement, row) for row in body]

        return self.insert_candles(points, measurement)
