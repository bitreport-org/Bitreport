from app.models import Series
from app.ta.indicators.custom import EWO, ICM, KC
from app.ta.indicators.talib import BB, EMA, MACD, MOM, OBV, RSI, SMA, STOCH, STOCHRSI

INDICATORS = {
    "KC": KC,
    "EWO": EWO,
    "ICM": ICM,
    "BB": BB,
    "EMA": EMA,
    "SMA": SMA,
    "RSI": RSI,
    "OBV": OBV,
    "MOM": MOM,
    "MACD": MACD,
    "STOCH": STOCH,
    "STOCHRSI": STOCHRSI,
}


def make_indicators(data: Series, limit: int):
    output = dict()
    for indicator in INDICATORS.values():
        output.update(indicator(data=data, limit=limit))

    return output
