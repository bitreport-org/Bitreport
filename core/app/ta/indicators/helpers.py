import logging
import traceback


from .custom import *
from .talib import *


def empty(keys: list) -> dict:
    d = {k: [] for k in keys}
    d['info'] = []
    return d


INDICATORS = {
    'KC': (KC, ['upper_band', 'middle_band', 'lower_band']),
    'EWO': (EWO, ['ewo']),
    'ICM': (ICM, ['leading_span_a', 'leading_span_b', 'base_line']),
    'BB': (BB, ['upper_band', 'middle_band', 'lower_band']),
    'EMA': (EMA, ['fast', 'medium', 'slow']),
    'SMA': (SMA, ['fast', 'medium', 'slow']),
    'RSI': (RSI, ['rsi']),
    'OBV': (OBV, ['obv']),
    'MOM': (MOM, ['mom']),
    'MACD': (MACD, ['macd', 'signal', 'histogram']),
    'STOCH': (STOCH, ['k', 'd']),
    'STOCHRSI': (STOCHRSI, ['k', 'd']),
}


def make_indicators(data: dict, limit: int):
    output = dict()
    # TODO: handle when there is less data then requested ! !
    for name, (f, default) in INDICATORS.items():
        try:
            output[name] = f(data, limit)
        # Broad exception because TA-Lib has low level
        # errors and because there's a lot of magic...
        except:
            logging.error(f'Indicator {name}, error: /n {traceback.format_exc()}')
            output[name] = empty(default)

    return output
