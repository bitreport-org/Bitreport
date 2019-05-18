from .custom import *
from .talib import *


INDICATORS = {
    'KC': KC,
    'EWO': EWO,
    'ICM': ICM,
    'BB': BB,
    'EMA': EMA,
    'SMA': SMA,
    'RSI': RSI,
    'OBV': OBV,
    'MOM': MOM,
    'MACD': MACD,
    'STOCH': STOCH,
    'STOCHRSI': STOCHRSI
}


def make_indicators(data: dict, limit: int):
    output = dict()
    for name, f in INDICATORS.items():
        output.update(f(data=data, limit=limit))

    return output
