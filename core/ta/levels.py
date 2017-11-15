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

def srlevels(data, p=80, pln=95):
    # Output: {'values': values, 'types' : types}
    # Remarks:
    #  strength in <0, 1> as a %
    #  var_type = 100 -> resistance
    #  var_type = -100 -> support
    close, open = data['close'], data['open']
    close = close[3:-3]
    open = open[3:-3]

    # Calculate p-th percentile of % change between two following candles
    average = []
    c = 0
    for i in range(1, close.size):
        average.append(abs(close[i] / close[i - 1] - 1))
    strength = np.percentile(average, p)

    support, resistance = [], []
    while c < close.size - 1:
        check = c
        if open[c + 1] > (1 + strength) * open[c]:
            resistance.append(followingMax(open[c:], 0)[0])
            c = c + followingMax(open[c:], strength)[1]
            # print('max' , c)

        elif close[c + 1] < (1 - strength) * close[c]:
            support.append(followingMin(close[c:], 0)[0])
            c = c + followingMin(close[c:], 0)[1]
            # print('min', c)

        if check == c:
            c += 1

    # calculate average candle lengtht
    average = []
    for i in range(1, close.size):
        average.append(abs(close[i] - close[i - 1]))
    strength = np.percentile(average, pln)

    # Remove levels which are to close
    i = 0
    resistance.sort(reverse=True)
    while i < len(resistance):
        j = i + 1
        m = 1
        while j < len(resistance):
            if abs(resistance[i] - resistance[j]) <= strength:
                resistance.remove(min(resistance[i], resistance[j]))
                m = 0
                break
            else:
                j += 1
        if m == 0:
            i = 0
        else:
            i += 1

    # Remove levels which are to close
    i = 0
    support.sort()
    while i < len(support):
        j = i + 1
        m = 1
        while j < len(support):
            if abs(support[i] - support[j]) <= strength:
                support.remove(max(support[i], support[j]))
                m = 0
                break
            else:
                j += 1
        if m == 0:
            i = 0
        else:
            i += 1

    return {'support': support, 'resistance': resistance}
