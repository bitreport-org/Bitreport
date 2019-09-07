# -*- coding: utf-8 -*-
import numpy as np
import talib  # pylint: skip-file

import config
from app.ta.helpers import indicator, nan_to_null

Config = config.BaseConfig()


# Elliott Wave Oscillator:
@indicator("EWO", ["ewo"])
def EWO(data, limit, fast=5, slow=35):
    start = Config.MAGIC_LIMIT
    close = data.close
    real = talib.EMA(close, fast) - talib.EMA(close, slow)
    return {"ewo": nan_to_null(real.tolist()[-limit:]), "info": []}


# Keltner channels:
@indicator("KC", ["upper_band", "middle_band", "lower_band"])
def KC(data, limit):
    # Keltner Channels
    # Middle Line: 20-day exponential moving average
    # Upper Channel Line: 20-day EMA + (2 x ATR(10))
    # Lower Channel Line: 20-day EMA - (2 x ATR(10))
    close = data.close
    high = data.high
    low = data.low

    mid = talib.SMA(close, 20)
    upperch = mid + (2 * talib.ATR(high, low, close, 10))
    lowerch = mid - (2 * talib.ATR(high, low, close, 10))

    return {
        "middle_band": nan_to_null(mid.tolist()[-limit:]),
        "upper_band": nan_to_null(upperch.tolist()[-limit:]),
        "lower_band": nan_to_null(lowerch.tolist()[-limit:]),
        "info": [],
    }


# Ichimoku Cloud:
@indicator("ICM", ["leading_span_a", "leading_span_b", "base_line"])
def ICM(data, limit):
    margin = Config.MARGIN
    high, low, close = data.high, data.low, data.close
    close_size = close.size

    # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
    n1 = 9
    conversion_line = [0] * (n1 - 1)
    for i in range(n1, close_size):
        conversion_line.append((np.max(high[i - n1 : i]) + np.min(low[i - n1 : i])) / 2)
    conversion_line = np.array(conversion_line)

    # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    n2 = 26
    base_line = [0] * (n2 - 1)
    for i in range(n2, close_size):
        base_line.append((np.max(high[i - n2 : i]) + np.min(low[i - n2 : i])) / 2)

    base_line = np.array(base_line)

    # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    leading_span_a = (conversion_line + base_line) / 2

    # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    n3 = 52
    leading_span_b = [0] * (n3 - 1)
    for i in range(n3, close_size):
        leading_span_b.append((np.max(high[i - n3 : i]) + np.min(low[i - n3 : i])) / 2)

    leading_span_b = np.array(leading_span_b)

    # Some magic
    leading_span_a = leading_span_a[-(limit + margin) :]
    leading_span_b = leading_span_b[-(limit + margin) :]

    # Tokens
    info = []
    actual_a = leading_span_a[-margin]
    actual_b = leading_span_b[-margin]
    if actual_a >= actual_b and close[-1] < actual_a:
        if close[-1] < actual_b:
            info.append("PIERCED_UP")
        else:
            info.append("IN_CLOUD_UP")

    elif actual_b > actual_a and close[-1] > actual_a:
        if close[-1] > actual_b:
            info.append("PIERCED_DOWN")
        else:
            info.append("IN_CLOUD_DOWN")

    width = np.abs(leading_span_a - leading_span_b)
    p1 = np.percentile(width, 0.80)
    p2 = np.percentile(width, 0.25)
    if width[-margin] >= p1:
        info.append("CLOUD_WIDE")
    elif width[-margin] <= p2:
        info.append("CLOUD_THIN")

    return {
        "leading_span_a": nan_to_null(leading_span_a.tolist()),
        "leading_span_b": nan_to_null(leading_span_b.tolist()),
        "base_line": nan_to_null(base_line.tolist()[-limit:]),
        "info": info,
    }
