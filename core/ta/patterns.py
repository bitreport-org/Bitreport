import talib
from services import internal


#FindPattern
#Input: dict, numpy array, talib pattern name, Bitfinex_numpy data
#Output: none
#Remarks: given dict is updated to form:
# { pattern1: { up: ['2017-09-17 20:00:00', '2017-09-24 20:00:00'], down: [2017-09-25 08:00:00'] } }
def FindPattern(dict, array, pattern_name, data):
    up = []
    down = []
    for i in range(0, array.size):
        if array[i] == 100:
            up.append(data['date'][i])
        elif array[i] == -100:
            down.append(data['date'][i])
    if up != [] and down != []:
        dict[pattern_name] = {'up': up, 'down': down}

#CheckAllPatterns
#Input: import_numpy
#Output: { pattern_name: { up: ['2017-09-17 20:00:00', '2017-09-24 20:00:00'], down: [2017-09-25 08:00:00' }, ...}
def CheckAllPatterns(data, patterns_list = 'none', all = 1):
    open = data['open']
    high = data['high']
    low = data['low']
    close = data['close']

    patterns = {}
    if all == 1:
        patterns_list = ['CDL2CROWS',
    'CDL3BLACKCROWS',
    'CDL3INSIDE',
    'CDL3LINESTRIKE',
    'CDL3OUTSIDE',
    'CDL3STARSINSOUTH',
    'CDL3WHITESOLDIERS',
    'CDLABANDONEDBABY',
    'CDLADVANCEBLOCK',
    'CDLBELTHOLD',
    'CDLBREAKAWAY',
    'CDLCLOSINGMARUBOZU',
    'CDLCONCEALBABYSWALL',
    'CDLCOUNTERATTACK',
    'CDLDARKCLOUDCOVER',
    'CDLDOJI',
    'CDLDOJISTAR',
    'CDLDRAGONFLYDOJI',
    'CDLENGULFING',
    'CDLEVENINGDOJISTAR',
    'CDLEVENINGSTAR',
    'CDLGAPSIDESIDEWHITE',
    'CDLGRAVESTONEDOJI',
    'CDLHAMMER',
    'CDLHANGINGMAN',
    'CDLHARAMI',
    'CDLHARAMICROSS',
    'CDLHIGHWAVE',
    'CDLHIKKAKE',
    'CDLHIKKAKEMOD',
    'CDLHOMINGPIGEON',
    'CDLIDENTICAL3CROWS',
    'CDLINNECK',
    'CDLINVERTEDHAMMER',
    'CDLKICKING',
    'CDLKICKINGBYLENGTH',
    'CDLLADDERBOTTOM',
    'CDLLONGLEGGEDDOJI',
    'CDLLONGLINE',
    'CDLMARUBOZU',
    'CDLMATCHINGLOW',
    'CDLMATHOLD',
    'CDLMORNINGDOJISTAR',
    'CDLMORNINGSTAR',
    'CDLONNECK',
    'CDLPIERCING',
    'CDLRICKSHAWMAN',
    'CDLRISEFALL3METHODS',
    'CDLSEPARATINGLINES',
    'CDLSHOOTINGSTAR',
    'CDLSHORTLINE',
    'CDLSPINNINGTOP',
    'CDLSTALLEDPATTERN',
    'CDLSTICKSANDWICH',
    'CDLTAKURI',
    'CDLTASUKIGAP',
    'CDLTHRUSTING',
    'CDLTRISTAR',
    'CDLUNIQUE3RIVER',
    'CDLXSIDEGAP3METHODS',
    'CDLXSIDEGAP3METHODS' ]

    for pattern in patterns_list:
        integer = getattr(talib,pattern)(open, high, low, close)
        FindPattern(patterns, integer, pattern, data)

    return patterns
