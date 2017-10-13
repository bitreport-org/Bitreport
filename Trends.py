from __future__ import print_function
import talib
import Bitfinex_API as ba
import pandas as pd
import numpy as np
from math import factorial
import matplotlib.pyplot as plt
import weasyprint
import datetime
from scipy.signal import argrelextrema
from scipy.cluster.vq import kmeans



def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError as msg:
        raise ValueError("window_size and order have to be of type int")

    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2

    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')

data = ba.Bitfinex_numpy('BTCUSD', '1D', 100)
close = data['close']
smooth_close = savitzky_golay(data['close'], 5, 3) # window size 51, polynomial order 3
'''
x=range(0,len(data['close']))
plt.plot(x, data['close'], 'r', x, smooth_close, 'b')
plt.show()


# SUPPORT AND RESISTANCE
support = []
resistance = []
for i in range(0, len(data['close'])-14):
    if smooth_close[i] < smooth_close[i+7] > smooth_close[i+14] and \
            ( smooth_close[i+7] / smooth_close[i+14]-1)>0.002:
        resistance.append(smooth_close[i+2])

    if smooth_close[i] > smooth_close[i+7] < smooth_close[i+14] and \
                    ( smooth_close[i+14] / smooth_close[i+7]-1)>0.002:
        support.append(smooth_close[i+2])

print('support', support)
print('resistance', resistance)
'''
'''
resistance = np.r_[True, close[1:] < close[:-1]] & np.r_[close[:-1] < close[1:], True]
print(resistance)
print(len(resistance))
'''



# for local maxima
resistance = close[argrelextrema(close, np.greater)[0]]
print(resistance)
resistance = np.sort(resistance)

import statistics

N = int(len(resistance)**0.5)+1
vmax = resistance[-1]
vmin = resistance[0]
len = vmax - vmin
h = len / N


l =[]
series = []
for i in range(1,N):
    for j in range (0, resistance.size):
        if (vmin + (i-1)*h) <= resistance[j] <= (vmin + i*h):
            l.append(resistance[j])
    series.append(l)
    #series.update({i:[statistics.mean(l), statistics.stdev(l)]})
    l = []


print(series)






# for local minima
support = close[argrelextrema(close, np.less)[0]]
print(support)