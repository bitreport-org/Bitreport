# -*- coding: utf-8 -*-
import requests

from .base import BaseExchange


class Bittrex(BaseExchange):
    timeframes = ["1h", "24h"]
    name = "Bittrex"
    pool = 2
    time_precision = "s"

    @staticmethod
    def _pair_format(pair: str) -> str:
        end_pair = pair[-3:]
        start_pair = pair[:-3]
        if end_pair == "USD":
            end_pair = end_pair + "T"
        return end_pair + "-" + start_pair

    def json(self, measurement: str, row: dict) -> dict:
        json_body = {
            "measurement": measurement,
            "tags": {"exchange": self.name.lower()},
            "time": row["T"],
            "fields": {
                "open": float(row["O"]),
                "close": float(row["C"]),
                "high": float(row["H"]),
                "low": float(row["L"]),
                "volume": float(row["BV"]),
            },
        }
        return json_body

    def fetch_candles(self, timeframe: str, limit: int = 0) -> bool:
        measurement = self.pair + timeframe
        pair_formated = self._pair_format(self.pair)

        timeframes = {"1h": "hour", "24h": "day"}
        btf = timeframes.get(timeframe, "1h")

        url = f"https://international.bittrex.com/Api/v2.0/pub/market/GetTicks"
        params = {"marketName": pair_formated, "tickInterval": btf}

        response = requests.get(url, params=params)
        body = response.json()

        # Check if response was successful
        if "success" not in body.keys() or response.status_code != 200:
            self.log_error(response)
            return False

        rows = body.get("result", False)

        if not rows:
            self.log_error(response)
            return False

        points = [self.json(measurement, row) for row in rows[-limit:]]

        return self.insert_candles(points, measurement)
