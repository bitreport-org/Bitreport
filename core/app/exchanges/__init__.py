# -*- coding: utf-8 -*-
from functools import reduce
from multiprocessing.dummy import Pool as ThreadPool
import threading
from influxdb import InfluxDBClient
import logging

from .binance import Binance
from .bitfinex import Bitfinex
from .bittrex import Bittrex
from .poloniex import Poloniex
from .helpers import check_exchanges, downsample_all_timeframes


def fill_pair(app, influx: InfluxDBClient,
              pair: str) -> tuple:
    """
    Retrieves data for a given pair from Binance, Bitfinex, Bittrex and Poloniex
    and inserts it to influx database. If it's needed a downsampling is being
    performed.

    Timeframes for each exchange:
    - Bitfinex 1h, 3h, 6h, 12h, 24h
    - Binance 1h, 2h, 6h, 12h, 24h
    - Bittrex 1h, 24h
    - Poloniex 30m, 2h, 24h

    Parameters
    ----------
    app: Flask app
    influx: instance of InfluxDBCLient
    pair: pair name ex. 'BTCUSD'

    Returns
    -------
    tuple (message, code)
    """

    if pair[:4] == 'TEST':
        return None, None

    exchanges = check_exchanges(influx, pair)

    fillers = dict(
        bitfinex=Bitfinex,
        bittrex=Bittrex,
        binance=Binance,
        poloniex=Poloniex
    )

    if exchanges:
        fillers = {k: v for k, v in fillers.items() if k in exchanges}

    pool = ThreadPool(4)
    results = pool.map(lambda filler: filler(influx).fill(pair), fillers.values())
    pool.close()
    pool.join()

    status = reduce(lambda x, y: x or y, results)
    exchanges_filled = [name for name, r in zip(fillers.keys(), results) if r]

    try:
        t = threading.Thread(target=downsample_all_timeframes, args=(influx, pair))
        t.start()
    except:
        pass

    if status:
        logging.info(f"{pair} filled from {', '.join(exchanges_filled)}")

        return f"{pair} filled from {', '.join(exchanges_filled)}", 200
    else:
        logging.error(f"{pair} failed to fill!")
        return f"{pair} failed to fill!", 202
