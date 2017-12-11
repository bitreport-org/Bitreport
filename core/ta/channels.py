import numpy as np
import talib

def talib_channel_front(data, start, percent=70):
    close, open, high, low = data['close'], data['open'], data['high'], data['low']
    avg = (close+open)/2

    length = int(percent/100 * close.size)

    probe_data = avg[:length]
    a = talib.LINEARREG_SLOPE(probe_data, length)[-1]
    b = talib.LINEARREG_INTERCEPT(probe_data, length)[-1]

    std = talib.STDDEV(avg, timeperiod=close.size, nbdev=0.5)[-1]

    up_channel, bottom_channel = [], []
    for i in range(close.size):
        up_channel.append(i*a+b+std)
        bottom_channel.append(i * a + b - std)

    return {'up': up_channel[start:], 'bottom':bottom_channel[start:]}