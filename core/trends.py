import Bitfinex_API as ba
import numpy as np
import talib
import matplotlib.pyplot as plt
import statistics

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

    levels = []

    for i in range(0, len(l)):
        levels.append( (l_pos[i], l[i], l_type[i]) )
    lvl = sorted(levels, key=lambda tup: tup[0])

    levels = []
    for i in range(0, len(lvl)):
        levels.append( {'position':lvl[i][0], 'value' : lvl[i][1], 'type' : lvl[i][2]} )

    return levels

# Elliott Wave Oscillator
def elliottWaveOscillator(data, fast = 5, slow = 35):
    close = data['close']
    return talib.EMA(close, fast) - talib.EMA(close, slow)

# Fire points
def FirePoint(data, power = 0.1):
    date, open, high, low, close = data['date'].tolist(), data['open'], data['high'], data['low'], data['close']
    dif = abs(open - close)
    avg = np.mean(dif)
    point = []
    for i in range(0, dif.size):
        if dif[i] >= (1+power)*avg:
            point.append({'index': i, 'date': date[i], 'value': dif[i], 'close': close[i]})
    return point

# #Channel

def channel(data, const = 1):
    ewo = elliottWaveOscillator(data).tolist()
    start = ewo[-1*const]
    minimum = start
    maximum = start

    positive = [] #list of last positive ewo value
    negative = [] # #list of last non-positive ewo value
    for i in range(0, len(ewo)-const+1):
        if ewo[i] > 0:
            positive.append(ewo[i])
        else:
            negative.append(ewo[i])

    if len(positive) > 0 and len(negative) > 0:
        print(1)
        if start <= 0 :
            positive.reverse()
            maximum = positive[0]
            for i in range(1, len(positive)):
                if maximum < positive[i]:
                    maximum = positive[i]

        if start > 0 :
            negative.reverse()
            minimum = negative[0]
            for i in range(1, len(negative)):
                if minimum > negative[i]:
                    minimum = negative[i]
    else:
        print(2)
        if len(positive) == 0:
                negative.reverse()
                minimum = negative[0]
                for i in range(1, len(negative)):
                    if minimum > negative[i]:
                        minimum = negative[i]
        elif len(negative) == 0:
            positive.reverse()
            maximum = positive[0]
            for i in range(1, len(positive)):
                if maximum < positive[i]:
                    maximum = positive[i]

    close = data['close']
    minindex = ewo.index(minimum)
    maxindex = ewo.index(maximum)

    channel_list = close[min(minindex, maxindex) : max(minindex, maxindex)]

    channel_dev = 0
    if len(channel_list) > 1:
        channel_dev = statistics.stdev(channel_list)


    return {'min_index': minindex , 'min_value': close[minindex],
            'max_index': maxindex, 'max_value': close[maxindex],
            'dev' : channel_dev} # assumes that ewo values are unique



