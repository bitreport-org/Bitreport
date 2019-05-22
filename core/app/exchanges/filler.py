# -*- coding: utf-8 -*-
from functools import reduce, partial
from multiprocessing.dummy import Pool as ThreadPool
from influxdb import InfluxDBClient
import logging

from .binance import Binance
from .bitfinex import Bitfinex
from .bittrex import Bittrex
from .poloniex import Poloniex
from .helpers import check_exchanges, downsample


def update_pair_data(influx: InfluxDBClient, pair: str) -> None:
    """
    1h or 30m timeframe data update
    """

    if pair[:4] == 'TEST':
        return None

    exchanges = check_exchanges(influx, pair)

    fillers = dict(
        bitfinex=partial(Bitfinex(influx).fetch_candles, timeframe='1h'),
        bittrex=partial(Bittrex(influx).fetch_candles, timeframe='1h'),
        binance=partial(Binance(influx).fetch_candles, timeframe='1h', limit=2),
        poloniex=partial(Poloniex(influx).fetch_candles, timeframe='30m')
    )

    if exchanges:
        fillers = {k: v for k, v in fillers.items() if k in exchanges}

    pool = ThreadPool(4)
    results = pool.map(lambda filler: filler(pair=pair), fillers.values())
    pool.close()
    pool.join()

    status = reduce(lambda x, y: x or y, results)
    exchanges_filled = [name for name, r in zip(fillers.keys(), results) if r]

    if status:
        logging.info(f"{pair} filled from {', '.join(exchanges_filled)}")
    else:
        logging.error(f"{pair} failed to fill!")

    # TODO: downsamples
    downsample(influx, pair, from_tf='30m', to_tf='1h')
    downsample(influx, pair, from_tf='1h', to_tf='2h')
    downsample(influx, pair, from_tf='1h', to_tf='3h')
    downsample(influx, pair, from_tf='1h', to_tf='4h')
    downsample(influx, pair, from_tf='1h', to_tf='6h')
    downsample(influx, pair, from_tf='1h', to_tf='12h')
    downsample(influx, pair, from_tf='1h', to_tf='24h')
