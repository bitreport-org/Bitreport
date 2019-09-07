import logging
from multiprocessing.dummy import Pool as ThreadPool
from typing import List

from requests import Response

from app.models.influx import insert_candles


class BaseExchange:
    pool = 4
    timeframes: list
    fetch_candles: callable
    name: str
    time_precision: str

    def __init__(self, pair: str):
        self.pair = pair

    def log_error(self, response: Response):
        logging.error(
            """Failed request, info:
        - exchange: %s
        - pair: %s
        - code: %s
        - body: %s
        """,
            self.name,
            self.pair,
            response.status_code,
            response.json(),
        )

    def insert_candles(self, points: List[dict], measurement: str):
        result = insert_candles(candles=points, time_precision=self.time_precision)
        if not result:
            logging.error(f"FAILED %s to write records for %s", self.name, measurement)
        return result

    def fill(self) -> bool:
        pool = ThreadPool(self.pool)
        results = pool.map(self.fetch_candles, self.timeframes)
        pool.close()
        pool.join()

        status = all(results)
        return status
