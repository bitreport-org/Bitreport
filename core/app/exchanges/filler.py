# -*- coding: utf-8 -*-
import logging
import threading
from multiprocessing.dummy import Pool as ThreadPool

from app.models.influx import check_exchanges, downsample_all_timeframes

from .binance import Binance
from .bitfinex import Bitfinex
from .bittrex import Bittrex
from .poloniex import Poloniex


def fill_pair(pair: str) -> tuple:
    """
    Retrieves data for a given pair from Binance, Bitfinex, Bittrex and Poloniex
    and inserts it to influx database.

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

    if pair.startswith("TEST"):
        return None, None

    exchanges = check_exchanges(pair)
    fillers = dict(
        bitfinex=Bitfinex, bittrex=Bittrex, binance=Binance, poloniex=Poloniex
    )

    if exchanges:
        fillers = {k: v for k, v in fillers.items() if k in exchanges}

    pool = ThreadPool(4)
    results = pool.map(lambda filler: filler(pair).fill(), fillers.values())

    pool.close()
    pool.join()

    status = any(results)
    exchanges_filled = [name for name, r in zip(fillers.keys(), results) if r]

    try:
        t = threading.Thread(target=downsample_all_timeframes, args=(pair,))
        t.start()
    except:  # pylint:disable=bare-except
        pass

    if not status:
        return f"{pair} failed to fill!", 202

    return f"{pair} filled from {', '.join(exchanges_filled)}", 200


def update_pair_data(pair: str) -> bool:
    """
    1h or 30m timeframe data update
    """

    if pair[:4] == "TEST":
        return False

    exchanges = check_exchanges(pair)

    fillers = (
        (Bitfinex, {"timeframe": "1h"}),
        (Bittrex, {"timeframe": "1h", "limit": 10}),
        (Binance, {"timeframe": "1h", "limit": 10}),
        (Poloniex, {"timeframe": "30m}"}),
    )

    if exchanges:
        fillers = [t for t in fillers if t[0].name.lower() in exchanges]

    def make_filler(input_data: tuple):
        filler, kwargs = input_data
        return filler(pair).fetch_candles(**kwargs)

    pool = ThreadPool(4)
    results = pool.map(make_filler, fillers)
    pool.close()
    pool.join()

    status = any(results)
    try:
        t = threading.Thread(target=downsample_all_timeframes, args=(pair,))
        t.start()
    except:  # pylint:disable=bare-except
        pass

    if not status:
        logging.error("%s failed to fill!", pair)
        return False

    return True
