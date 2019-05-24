# -*- coding: utf-8 -*-
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool
from influxdb import InfluxDBClient
import logging
import threading

from .binance import Binance
from .bitfinex import Bitfinex
from .bittrex import Bittrex
from .poloniex import Poloniex
from .helpers import check_exchanges, downsample_all_timeframes


def update_pair_data(influx: InfluxDBClient, pair: str) -> bool:
    """
    1h or 30m timeframe data update
    """

    if pair[:4] == 'TEST':
        return None

    exchanges = check_exchanges(influx, pair)

    fillers = dict(
        bitfinex=partial(Bitfinex(influx).fetch_candles, timeframe='1h'),
        bittrex=partial(Bittrex(influx).fetch_candles, timeframe='1h'),
        binance=partial(Binance(influx).fetch_candles, timeframe='1h', limit=3),
        poloniex=partial(Poloniex(influx).fetch_candles, timeframe='30m')
    )

    if exchanges:
        fillers = {k: v for k, v in fillers.items() if k in exchanges}

    pool = ThreadPool(4)
    results = pool.map(lambda filler: filler(pair), fillers.values())
    pool.close()
    pool.join()

    status = any(results)
    exchanges_filled = [name for name, r in zip(fillers.keys(), results) if r]

    try:
        t = threading.Thread(target=downsample_all_timeframes, args=(influx, pair))
        t.start()
    except:
        pass

    if status:
        logging.info(f"{pair} filled from {', '.join(exchanges_filled)}")
        return True
    else:
        logging.error(f"{pair} failed to fill!")
        return False