from __future__ import print_function
import Bitfinex_API as ba
import numpy as np
import talib
import matplotlib.pyplot as plt

# followingMax finds first maximum in close
# Input: (Bitfinex_numpy['close'], strength) the strength determinates how pointed maximas must be
# Output: [max , max_position_in_close]
# Remarks: strength in <0, 1> as a %
def followingMax(close, strength):
    max = close[0]
    max_pos = 0
    for i in range(0, close.size-1):
        if close[i+1] > (1 + strength) * close[i]:
            max = close[i+1]
            max_pos = i+1
        else:
            break
    return [max, max_pos]

# followingMin finds first minimum in close
# Input: (Bitfinex_numpy['close'], strength) the strength determinates how pointed minimas must be
# Output: [min , min_position_in_close]
# Remarks:strength in <0, 1> as a %
def followingMin(close, strength):
    min = close[0]
    min_pos = 0
    for i in range(0, close.size-1):
        if close[i+1] < (1 - strength) * close[i]:
            min = close[i+1]
            min_pos= i+1
        else:
            break
    return [min, min_pos]

# Levels finds support and resistance [levels, position]
# Input: (Bitfinex_numpy['close'], strength) the strength determinates how pointed extremas must be
# Output: [[var1, var2,... ], [var1_position_in_close, ...]]
# Remarks:strength in <0, 1> as a %
def Levels(close, strength=0):
    l =[]
    l_pos = []
    c=0
    while c < close.size-1:
        if close[c+1] >= close[c]:
            l.append(followingMax(close[c:], strength)[0])
            l_pos.append(c + followingMax(close[c:], strength)[1])
            c = c + followingMax(close[c:], strength)[1]

        elif close[c+1] < close[c]:
            l.append(followingMin(close[c:], strength)[0])
            l_pos.append(c + followingMin(close[c:], strength)[1])
            c = c + followingMin(close[c:], strength)[1]


    return [l, l_pos]





# # Example data
# data = ba.Bitfinex_numpy('BTCUSD', '3h', 100)
# close = data['close']
#
# rs = Levels(close,0)
#
# x=range(0,data['close'].size)
#
# fig = plt.figure(figsize=(10,6))
#
# for j in range(0, len(rs[1])):
#     plt.plot(x, np.array([rs[0][j] for i in x]), 'g')
#
# plt.plot(x, data['close'], 'r')
# plt.show()

