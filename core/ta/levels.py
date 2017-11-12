import numpy as np
import talib
import statistics


def followingMax(close, strength):
    # followingMax finds first maximum in close
    # Input: (Bitfinex_numpy['close'], strength) the strength determinates how pointed maximas must be
    # Output: [max , max_position_in_close]
    # Remarks: strength in <0, 1> as a %
    max = close[0]
    max_pos = 0
    for i in range(0, close.size-1):
        if close[i+1] > (1 + strength) * close[i]:
            max = close[i+1]
            max_pos = i+1
        else:
            break
    return [max, max_pos]

def followingMin(close, strength):
    # followingMin finds first minimum in close
    # Input: (Bitfinex_numpy['close'], strength) the strength determinates how pointed minimas must be
    # Output: [min , min_position_in_close]
    # Remarks:strength in <0, 1> as a %

    min = close[0]
    min_pos = 0
    for i in range(0, close.size-1):
        if close[i+1] < (1 - strength) * close[i]:
            min = close[i+1]
            min_pos= i+1
        else:
            break
    return [min, min_pos]

def srlevels(data, strength=0.03):
    # Levels finds support and resistance [levels, position]
    # Input: (Bitfinex_numpy['close'], strength) the strength determinates how pointed extremas must be
    # Output: [[var1, var2,... ], [var1_position_in_close, ...], [var1_type,...]]
    # Remarks:
    #           strength in <0, 1> as a %
    #           var_type = 100 -> resistance
    #           var_type = -100 -> support
    close = data['close']
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

        elif close[c+1] < (1 - strength) *close[c]:
            l.append(followingMin(close[c:], 0)[0])
            l_pos.append(c + followingMin(close[c:], 0)[1])
            l_type.append(-100)
            c = c + followingMin(close[c:], 0)[1]

        if check == c:
            c += 1

    levels = []

    for i in range(0, len(l)):
        levels.append( (l_pos[i], l[i], l_type[i]) )
    lvl = sorted(levels, key=lambda tup: tup[0])

    sup = []
    res =[]

    # 'position':lvl[i][0]
    for i in range(0, len(lvl)):
        if lvl[i][2] == -100: # type = support
            sup.append(lvl[i][1]) # append value
        else:
            res.append(lvl[i][1]) # append value

    return {'support': sup, 'resistance': res}