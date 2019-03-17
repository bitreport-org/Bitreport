# -*- coding: utf-8 -*-
from .binance import Binance
from .bitfinex import Bitfinex
from .bittrex import Bittrex
from .poloniex import Poloniex

from functools import reduce
from multiprocessing.dummy import Pool as ThreadPool
from influxdb import InfluxDBClient

def fill_pair(influx: InfluxDBClient, pair: str) -> tuple:
    """
    Retrieves data for a given pair from Binance, Bitfinex, Bittrex and Poloniex
    and inserts it to influx database. If it's needed a downsampling is being
    performed.

    Timeframes for each exchange:
    - Bitfinex 1h, 3h, 6h, 12h, 24h
    - Binance 1h, 2h, 6h, 12h, 24h
    - Bittrex 1h, 24h
    - Poloniex 30m, 2h, 24h

    :param influx: instance of InfluxDBCLient
    :param pair: pair name ex. 'BTCUSD'
    :return: tuple (message, code)
    """

    fillers = dict(
        bitfinex=Bitfinex,
        bittrex=Bittrex,
        binance=Binance,
        poloniex=Poloniex
    )

    pool = ThreadPool(4)
    results = pool.map(lambda filler: filler(influx).fill(pair), fillers.values())
    pool.close()
    pool.join()

    status = reduce(lambda x,y : x or y, results)
    exchanges_filled = [name for name, r in zip(fillers.keys(), results) if r]

    if status:
        return f"{pair} filled from {', '.join(exchanges_filled)}", 200
    else:
        return f"{pair} failed to fill!", 404
