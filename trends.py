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
# Output: [[var1, var2,... ], [var1_position_in_close, ...], [var1_type,...]]
# Remarks:
#           strength in <0, 1> as a %
#           var_type = 100 -> resistance
#           var_type = -100 -> support
def Levels(close, strength=0.0):
    l =[]
    l_pos = []
    l_type = []
    c=0
    while c < close.size-1:
        check = c
        if close[c+1] > (1 + strength) * close[c]:
            l.append(followingMax(close[c:], 0)[0])
            l_pos.append(c + followingMax(close[c:], 0)[1])
            l_type.append(100)
            c = c + followingMax(close[c:], strength)[1]
            #print('max' , c)

        elif close[c+1] < (1 - strength) *close[c]:
            l.append(followingMin(close[c:], 0)[0])
            l_pos.append(c + followingMin(close[c:], 0)[1])
            l_type.append(-100)
            c = c + followingMin(close[c:], 0)[1]
            #print('min', c)

        if check == c:
            c += 1
            #print('neutral',c)

    return [l, l_pos, l_type]





# Example data
# pair, period = 'ETPUSD', '1h'
#
# data = ba.Bitfinex_numpy(pair, period, 60)
#
# close = data['close']
# rs = Levels(close, 0.06)
# print(rs)



