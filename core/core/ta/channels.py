import numpy as np
import talib

def channel(data, magic_limit, margin=26,percent=70):
    close, open, high, low = data['close'], data['open'], data['high'], data['low']
    avg = (close+open)/2

    length = int(percent/100 * close.size)

    probe_data = avg[:length]
    a = talib.LINEARREG_SLOPE(probe_data, length)[-1]
    b = talib.LINEARREG_INTERCEPT(probe_data, length)[-1]

    std = talib.STDDEV(avg, timeperiod=close.size, nbdev=0.5)[-1]

    up_channel, bottom_channel , channel= [], [], []
    for i in range(close.size+margin):
        up_channel.append(i*a+b+std)
        bottom_channel.append(i * a + b - std)
        channel.append(i * a + b)


    return {'upperband': up_channel[magic_limit:], 'middleband': channel[magic_limit:],'lowerband':bottom_channel[magic_limit:]}


def parabola(data, magic_limit, margin=26):
    open = data['open']
    close = data['close']

    avg = (open+close)/2

    # mini = talib.MININDEX(close, open.size)[-1]
    # maxi = talib.MAXINDEX(close, open.size)[-1]

    start = 0 # min(mini,maxi)
    end = close.size # max(mini,maxi)+1

    x = np.array(range(start, end))
    longer_x = np.array(range(close.size+margin))

    y = avg # [start : end]

    # creates parabola polynomial
    poly = np.poly1d(np.polyfit(x, y, 2))

    vector = 0 # poly(start) - open[start]
    std = talib.STDDEV(y, timeperiod=y.size, nbdev=1)[-1]

    z, zp, zm = [], [], []
    for point in longer_x:
        z.append(poly(point)-vector)
        zm.append(poly(point) - vector-std)
        zp.append(poly(point) - vector+std)

    return {'middleband': z[magic_limit:], 'upperband': zp[magic_limit:], 'lowerband':zm[magic_limit:]}

def linear(data, magic_limit, period = 20):
    close = data['close']

    indicator_values = [0] * period
    up_channel, bottom_channel = [0] * period, [0] * period

    for i in range(period,close.size):
        probe_data = close[i-period : i]
        a = talib.LINEARREG_SLOPE(probe_data, period)[-1]
        b = talib.LINEARREG_INTERCEPT(probe_data, period)[-1]
        y = a*period+b
        std = talib.STDDEV(probe_data, timeperiod=probe_data.size, nbdev=1)[-1]

        indicator_values.append(y)
        up_channel.append(y + std)
        bottom_channel.append(y - std)

    return {'upperband': up_channel[magic_limit:], 'middleband':indicator_values[magic_limit:], 'lowerband': bottom_channel[magic_limit:]}