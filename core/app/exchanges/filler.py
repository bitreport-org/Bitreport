# -*- coding: utf-8 -*-
from functools import partial
from multiprocessing.dummy import Pool as ThreadPool
from flask import current_app

import logging
import threading

from .binance import Binance
from .bitfinex import Bitfinex
from .bittrex import Bittrex
from .poloniex import Poloniex
from .helpers import check_exchanges, downsample_all_timeframes


def update_pair_data(pair: str) -> bool:
    """
    1h or 30m timeframe data update
    """

    if pair[:4] == 'TEST':
        return False

    exchanges = check_exchanges(pair)

    fillers = dict(
        bitfinex=partial(Bitfinex().fetch_candles, timeframe='1h'),
        bittrex=partial(Bittrex().fetch_candles, timeframe='1h', limit=10),
        binance=partial(Binance().fetch_candles, timeframe='1h', limit=10),
        poloniex=partial(Poloniex().fetch_candles, timeframe='30m')
    )

    if exchanges:
        fillers = {k: v for k, v in fillers.items() if k in exchanges}

    ctx = current_app.app_context()

    def ctx_filler(filler):
        with ctx:
            result = filler(pair)
        return result

    pool = ThreadPool(4)
    results = pool.map(ctx_filler, fillers.values())
    pool.close()
    pool.join()

    status = any(results)
    exchanges_filled = [name for name, r in zip(fillers.keys(), results) if r]

    try:
        t = threading.Thread(target=downsample_all_timeframes, args=(ctx, pair))
        t.start()
    except:
        pass

    if not status:
        logging.error(f"{pair} failed to fill!")
        return False

    logging.info(f"{pair} filled from {', '.join(exchanges_filled)}")
    return True
