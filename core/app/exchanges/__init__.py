# -*- coding: utf-8 -*-
from .binance import Binance
from .bitfinex import Bitfinex
from .bittrex import Bittrex
from .poloniex import Poloniex

import logging

def fill_pair(influx, pair, exchange):
    """
    Bitfinex 1h, 3h, 6h, 12h, 24h
    Binance 1h, 2h, 6h, 12h, 24h
    Bittrex 1h, 24h
    """

    fillers = dict(
        bitfinex=Bitfinex,
        bittrex=Bittrex,
        binance=Binance,
        poloniex=Poloniex
    )

    if exchange not in fillers.keys():
        msg = f'{exchange} exchange does not exist'
        logging.error(f'{exchange} exchange does not exist')
        return msg, 404

    filler = fillers[exchange]
    status = filler(influx).fill(pair)

    if status:
        return f"{pair} filled from {exchange}", 200
    else:
        return f"{pair} failed to fill from {exchange}", 404


def check_exchange(influx, pair: str):
    pair = pair.upper()
    history = [ex(influx).check(pair) for ex in [Bittrex, Bitfinex, Poloniex, Binance]]
    history.sort(key=lambda x: x[1])
    history = [(name, value) for name, value in history if value>0]

    if len(history) > 0:
        return history[-1][0], 200
    else:
        return 'Exchange not found...', 404