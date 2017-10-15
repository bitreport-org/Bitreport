from __future__ import print_function
import talib
import Bitfinex_API as ba
import pandas as pd
import weasyprint
import datetime


# RSI info
def RSI_info(close, time=14):
    rsi = talib.RSI(close, time)
    info1 = ''
    if rsi[-1] > 80:
        info1 = ", Overbuy"
    elif rsi[-1] < 40:
        info1 = ', Oversold'

    if rsi[-1]-rsi[-6] >0:
        info2 = ', uptrend over 5 periods'
    else:
        info2 = ', downtrend over 5 periods'

    return "Wartość RSI: " +  str("%.2f" % rsi[-1]) + info1 + info2

# MACD info
def MACD_info(close, fast = 12, slow = 26, signal = 9):
    macd, macdsignal, macdhist = talib.MACD(close, slow, fast, signal)

    if macd[-1]-[-6] > 0:
        info1 = 'MACD uptrend, '
    else:
        info1 = 'MACD downtrend, '

    if macdsignal[-1]-[-6] > 0:
        info2 = 'Signal uptrend, '
    else:
        info2 = 'Signal downtrend'

    return info1 + info2 +'Histogram: ' + str("%.7f" % macdhist[-1])

#OBV info
def OBV_info(close, volume):
    real = talib.OBV(close, volume)
    if real[-1]- real[-24] > 0 :
        info = 'uptrend 24h, '
    else:
        info = 'downtrend 24h, '

    return info + 'OBV :' + str("%.1f" % real[-1])

#BB info
def BB_info(close, timeperiod=20, nbdevup=2, nbdevdn=2):
    upperband, middleband, lowerband = talib.BBANDS(close, timeperiod, nbdevup, nbdevdn, matype=0)
    info1 = ''
    if close[-1]-upperband[-1] >= 0:
        info1 = 'over the upper band ,'
    elif close[-1]- lowerband[-1] <= 0:
         info1 = 'under the lower band, '

    if (close[-1]-middleband[-1]) >= 0:
        info2 = 'over the SMA, dist: ' + str("%.5f" % (close[-1]-middleband[-1]))
    else:
        info2 = 'under the SMA, dist: ' + str("%.5f" % (close[-1]-middleband[-1]))

    # Squeeze

    return info1  + info2  + ', '  + 'SMA value: ' + str("%.5f" % (middleband[-1]))

def Pair_info(pair, period, limit):
    candles = ba.Bitfinex_numpy(pair, period, limit)
    # Numpy array format needed to perform TA-lib indicators
    date = candles['date']
    open = candles['open']
    close = candles['close']
    high = candles['high']
    low = candles['low']
    volume = candles['volume']
    last_info = date[-1] + ' O: ' + str("%.5f" % open[-1]) + ' H: ' + str( "%.5f" % high[-1]) + \
                 ' L: ' + str("%.5f" % low[-1]) + ' C: ' + str("%.5f" % close[-1])

    list = [period, last_info, RSI_info(close, time=14), MACD_info(close, fast=12, slow=26, signal=9),
            OBV_info(close, volume), BB_info(close, timeperiod=20, nbdevup=2, nbdevdn=2), 'Reco']

    return list

# Input: [period1, perio2, ...],  pair
# output: pndas datafrme
def Bitfinex_info(periods, pair):
    pd.options.display.max_colwidth = 1000
    list = []
    for period in periods:
        list.append(Pair_info(pair, period, 50))
    return pd.DataFrame.from_records(list, columns=['Timeframe','Overal', 'RSI', 'MACD', 'OBV', 'BB', 'Reco'])



#--------------- JINJA REPORT PDF ---------------
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('.'))



#paramteres
pairs = ['BTCUSD','NEOBTC', 'OMGBTC', 'ETHUSD', 'LTCUSD', 'ETPUSD']
periods = ['1h', '6h', '1D']
filename = 'Report '+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")



template_dict = {"report_title": filename}
for i in range(0, len(pairs)):
    template_dict[pairs[i]] = pairs[i]
    template_dict[pairs[i] + '_table'] = Bitfinex_info(periods, pairs[i]).to_html()


template = env.get_template("myreport.html")
html_out = template.render(template_dict)
weasyprint.HTML(string=html_out).write_pdf("report.pdf", stylesheets=["typography.css"])

Html_file= open("strona.html","w")
Html_file.write(html_out)
Html_file.close()

