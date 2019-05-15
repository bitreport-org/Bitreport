import logging
import traceback


from .custom import *
from .talib import *

default_band = {
    'upper_band': [],
    'middle_band': [],
    'lower_band': [],
    'info': []
}


def empty(keys: list) -> dict:
    d = {k: [] for k in keys}
    d['info'] = []
    return d


INDICATORS = {
    'KC': (KC, default_band),
    'EWO': (EWO, empty(['ewo'])),
    'ICM': (ICM, empty(['leading_span_a', 'leading_span_b', 'base_line'])),
    'BB': (BB, default_band),
    'EMA': (EMA, empty(['fast', 'medium', 'slow'])),
    'SMA': (SMA, empty(['fast', 'medium', 'slow'])),
    'RSI': (RSI, empty(['rsi'])),
    'OBV': (OBV, empty(['obv'])),
    'MOM': (MOM, empty(['mom'])),
    'MACD': (MACD, empty(['macd', 'signal', 'histogram'])),
    'STOCH': (STOCH, empty(['k', 'd'])),
    'STOCHRSI': (STOCHRSI, empty(['k', 'd'])),
}


def make_indicators(data: dict):
    output = dict()
    for name, (f, default) in INDICATORS.items():
        try:
            output[name] = f(data)
        # Broad exception because TA-Lib has low level
        # errors and because there's a lot of magic...
        except:
            logging.error(f'Indicator {name}, error: /n {traceback.format_exc()}')
            output[name] = default

    return output
