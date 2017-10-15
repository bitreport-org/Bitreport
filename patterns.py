import Bitfinex_API as ba
import talib




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
#Input: Bitfinex_numpy
#Output: { pattern_name: { up: ['2017-09-17 20:00:00', '2017-09-24 20:00:00'], down: [2017-09-25 08:00:00' }, ...}
def CheckAllPatterns(data):
    open = data['open']
    high = data['high']
    low = data['low']
    close = data['close']

    patterns = {}

    #CDL2CROWS - Two Crows
    integer = talib.CDL2CROWS(open, high, low, close)
    pattern_name = 'CDL2CROWS'
    FindPattern(patterns, integer, pattern_name, data)


    #CDL3BLACKCROWS - Three Black Crows
    integer = talib.CDL3BLACKCROWS(open, high, low, close)
    pattern_name = 'CDL3BLACKCROWS'
    FindPattern(patterns, integer, pattern_name, data)


    #CDL3INSIDE - Three Inside Up/Down
    integer = talib.CDL3INSIDE(open, high, low, close)
    pattern_name = 'CDL3INSIDE'
    FindPattern(patterns, integer, pattern_name, data)


    #CDL3LINESTRIKE - Three-Line Strike
    integer = talib.CDL3LINESTRIKE(open, high, low, close)
    pattern_name = 'CDL3LINESTRIKE'
    FindPattern(patterns, integer, pattern_name, data)


    #CDL3OUTSIDE - Three Outside Up/Down
    integer = talib.CDL3OUTSIDE(open, high, low, close)
    pattern_name = 'CDL3OUTSIDE'
    FindPattern(patterns, integer, pattern_name, data)


    #CDL3STARSINSOUTH - Three Stars In The South
    integer = talib.CDL3STARSINSOUTH(open, high, low, close)
    pattern_name = 'CDL3STARSINSOUTH'
    FindPattern(patterns, integer, pattern_name, data)


    #CDL3WHITESOLDIERS - Three Advancing White Soldiers
    integer = talib.CDL3WHITESOLDIERS(open, high, low, close)
    pattern_name = 'CDL3WHITESOLDIERS'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLABANDONEDBABY - Abandoned Baby
    integer = talib.CDLABANDONEDBABY(open, high, low, close, penetration=0)
    pattern_name = 'CDLABANDONEDBABY'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLADVANCEBLOCK - Advance Block
    integer = talib.CDLADVANCEBLOCK(open, high, low, close)
    pattern_name = 'CDLADVANCEBLOCK'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLBELTHOLD - Belt-hold
    integer = talib.CDLBELTHOLD(open, high, low, close)
    pattern_name = 'CDLBELTHOLD'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLBREAKAWAY - Breakaway
    integer = talib.CDLBREAKAWAY(open, high, low, close)
    pattern_name = 'CDLBREAKAWAY'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLCLOSINGMARUBOZU - Closing Marubozu
    integer = talib.CDLCLOSINGMARUBOZU(open, high, low, close)
    pattern_name = 'CDLCLOSINGMARUBOZU'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLCONCEALBABYSWALL - Concealing Baby Swallow
    integer = talib.CDLCONCEALBABYSWALL(open, high, low, close)
    pattern_name = 'CDLCONCEALBABYSWALL'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLCOUNTERATTACK - Counterattack
    integer = talib.CDLCOUNTERATTACK(open, high, low, close)
    pattern_name = 'CDLCOUNTERATTACK'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLDARKCLOUDCOVER - Dark Cloud Cover
    integer = talib.CDLDARKCLOUDCOVER(open, high, low, close, penetration=0)
    pattern_name = 'CDLDARKCLOUDCOVER'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLDOJI - Doji
    integer = talib.CDLDOJI(open, high, low, close)
    pattern_name = 'CDLDOJI'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLDOJISTAR - Doji Star
    integer = talib.CDLDOJISTAR(open, high, low, close)
    pattern_name = 'CDLDOJISTAR'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLDRAGONFLYDOJI - Dragonfly Doji
    integer = talib.CDLDRAGONFLYDOJI(open, high, low, close)
    pattern_name = 'CDLDRAGONFLYDOJI'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLENGULFING - Engulfing Pattern
    integer = talib.CDLENGULFING(open, high, low, close)
    pattern_name = 'CDLENGULFING'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLEVENINGDOJISTAR - Evening Doji Star
    integer = talib.CDLEVENINGDOJISTAR(open, high, low, close, penetration=0)
    pattern_name = 'CDLEVENINGDOJISTAR'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLEVENINGSTAR - Evening Star
    integer = talib.CDLEVENINGSTAR(open, high, low, close, penetration=0)
    pattern_name = 'CDLEVENINGSTAR'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLGAPSIDESIDEWHITE - Up/Down-gap side-by-side white lines
    integer = talib.CDLGAPSIDESIDEWHITE(open, high, low, close)
    pattern_name = 'DLGAPSIDESIDEWHITE'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLGRAVESTONEDOJI - Gravestone Doji
    integer = talib.CDLGRAVESTONEDOJI(open, high, low, close)
    pattern_name = 'CDLGRAVESTONEDOJI'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLHAMMER - Hammer
    integer = talib.CDLHAMMER(open, high, low, close)
    pattern_name = 'CDLHAMMER'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLHANGINGMAN - Hanging Man
    integer = talib.CDLHANGINGMAN(open, high, low, close)
    pattern_name = 'CDLHANGINGMAN'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLHARAMI - Harami Pattern
    integer = talib.CDLHARAMI(open, high, low, close)
    pattern_name = 'CDLHARAMI'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLHARAMICROSS - Harami Cross Pattern
    integer = talib.CDLHARAMICROSS(open, high, low, close)
    pattern_name = 'CDLHARAMICROSS'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLHIGHWAVE - High-Wave Candle
    integer = talib.CDLHIGHWAVE(open, high, low, close)
    pattern_name = 'CDLHIGHWAVE'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLHIKKAKE - Hikkake Pattern
    integer = talib.CDLHIKKAKE(open, high, low, close)
    pattern_name = 'CDLHIKKAKE'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLHIKKAKEMOD - Modified Hikkake Pattern
    integer = talib.CDLHIKKAKEMOD(open, high, low, close)
    pattern_name = 'CDLHIKKAKEMOD'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLHOMINGPIGEON - Homing Pigeon
    integer = talib.CDLHOMINGPIGEON(open, high, low, close)
    pattern_name = 'CDLHOMINGPIGEON'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLIDENTICAL3CROWS - Identical Three Crows
    integer = talib.CDLIDENTICAL3CROWS(open, high, low, close)
    pattern_name = 'CDLIDENTICAL3CROWS'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLINNECK - In-Neck Pattern
    integer = talib.CDLINNECK(open, high, low, close)
    pattern_name = 'CDLINNECK'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLINVERTEDHAMMER - Inverted Hammer
    integer = talib.CDLINVERTEDHAMMER(open, high, low, close)
    pattern_name = 'CDLINVERTEDHAMMER'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLKICKING - Kicking
    integer = talib.CDLKICKING(open, high, low, close)
    pattern_name = 'CDLKICKING'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLKICKINGBYLENGTH - Kicking - bull/bear determined by the longer marubozu
    integer = talib.CDLKICKINGBYLENGTH(open, high, low, close)
    pattern_name = 'CDLKICKINGBYLENGTH'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLLADDERBOTTOM - Ladder Bottom
    integer = talib.CDLLADDERBOTTOM(open, high, low, close)
    pattern_name = 'CDLLADDERBOTTOM'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLLONGLEGGEDDOJI - Long Legged Doji
    integer = talib.CDLLONGLEGGEDDOJI(open, high, low, close)
    pattern_name = 'CDLLONGLEGGEDDOJI'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLLONGLINE - Long Line Candle
    integer = talib.CDLLONGLINE(open, high, low, close)
    pattern_name = 'CDLLONGLINE'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLMARUBOZU - Marubozu
    integer = talib.CDLMARUBOZU(open, high, low, close)
    pattern_name = 'CDLMARUBOZU'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLMATCHINGLOW - Matching Low
    integer = talib.CDLMATCHINGLOW(open, high, low, close)
    pattern_name = 'CDLMATCHINGLOW'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLMATHOLD - Mat Hold
    integer = talib.CDLMATHOLD(open, high, low, close, penetration=0)
    pattern_name = 'CDLMATHOLD'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLMORNINGDOJISTAR - Morning Doji Star
    integer = talib.CDLMORNINGDOJISTAR(open, high, low, close, penetration=0)
    pattern_name = 'CDLMORNINGDOJISTAR'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLMORNINGSTAR - Morning Star
    integer = talib.CDLMORNINGSTAR(open, high, low, close, penetration=0)
    pattern_name = 'CDLMORNINGSTAR'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLONNECK - On-Neck Pattern
    integer = talib.CDLONNECK(open, high, low, close)
    pattern_name = 'CDLONNECK'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLPIERCING - Piercing Pattern
    integer = talib.CDLPIERCING(open, high, low, close)
    pattern_name = 'CDLPIERCING'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLRICKSHAWMAN - Rickshaw Man
    integer = talib.CDLRICKSHAWMAN(open, high, low, close)
    pattern_name = 'CDLRICKSHAWMAN'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLRISEFALL3METHODS - Rising/Falling Three Methods
    integer = talib.CDLRISEFALL3METHODS(open, high, low, close)
    pattern_name = 'CDLRISEFALL3METHODS'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLSEPARATINGLINES - Separating Lines
    integer = talib.CDLSEPARATINGLINES(open, high, low, close)
    pattern_name = 'CDLSEPARATINGLINES'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLSHOOTINGSTAR - Shooting Star
    integer = talib.CDLSHOOTINGSTAR(open, high, low, close)
    pattern_name = 'CDLSHOOTINGSTAR'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLSHORTLINE - Short Line Candle
    integer = talib.CDLSHORTLINE(open, high, low, close)
    pattern_name = 'CDLSHORTLINE'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLSPINNINGTOP - Spinning Top
    integer = talib.CDLSPINNINGTOP(open, high, low, close)
    pattern_name = 'CDLSPINNINGTOP'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLSTALLEDPATTERN - Stalled Pattern
    integer = talib.CDLSTALLEDPATTERN(open, high, low, close)
    pattern_name = 'CDLSTALLEDPATTERN'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLSTICKSANDWICH - Stick Sandwich
    integer = talib.CDLSTICKSANDWICH(open, high, low, close)
    pattern_name = 'CDLSTICKSANDWICH'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLTAKURI - Takuri (Dragonfly Doji with very long lower shadow)
    integer = talib.CDLTAKURI(open, high, low, close)
    pattern_name = 'CDLTAKURI'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLTASUKIGAP - Tasuki Gap
    integer = talib.CDLTASUKIGAP(open, high, low, close)
    pattern_name = 'CDLTASUKIGAP'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLTHRUSTING - Thrusting Pattern
    integer = talib.CDLTHRUSTING(open, high, low, close)
    pattern_name = 'CDLTHRUSTING'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLTRISTAR - Tristar Pattern
    integer = talib.CDLTRISTAR(open, high, low, close)
    pattern_name = 'CDLTRISTAR'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLUNIQUE3RIVER - Unique 3 River
    integer = talib.CDLUNIQUE3RIVER(open, high, low, close)
    pattern_name = 'CDLUNIQUE3RIVER'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLXSIDEGAP3METHODS - Upside Gap Two Crows
    integer = talib.CDLUPSIDEGAP2CROWS(open, high, low, close)
    pattern_name = 'CDLXSIDEGAP3METHODS'
    FindPattern(patterns, integer, pattern_name, data)


    #CDLXSIDEGAP3METHODS - Upside/Downside Gap Three Methods
    integer = talib.CDLXSIDEGAP3METHODS(open, high, low, close)
    pattern_name = 'CDLXSIDEGAP3METHODS'
    FindPattern(patterns, integer, pattern_name, data)

    return patterns



# Example data
# data = ba.Bitfinex_numpy('BTCUSD', '6h', 300)
# print(CheckAllPatterns(data))