import numpy as np
import time
from requests import put
import datetime
import talib
import logging

from services import internal


def check_bb(data):
    close = data['close']
    upperband, middleband, lowerband = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    up = upperband.tolist()[-1]
    low = lowerband.tolist()[-1]
    close1 = close[-1]

    if close1 > up:
        return 'UP'
    elif close1 < low:
        return 'DOWN'

    return False


def check_sma(data):
    close = data['close']
    sma = talib.SMA(close, timeperiod=20)[-1]

    close1 = close[-1]
    close2 = close[-2]

    if close1 > sma > close2:
        return 'UP'
    elif close1 < sma < close2:
        return 'DOWN'

    return False


def check_dildo(data):
    open, close = data['open'], data['close']
    probe = abs(open-close)
    #avg = np.mean(probe)
    avg = np.percentile(probe, 80)

    diff = close[-1] - open[-1]
    adiff = abs(diff)
    if diff >= avg:
        return 'UP'
    elif diff < 0 and adiff >= avg:
        return 'DOWN'

    return False


def update_events():
    conf = internal.Config('config.ini', 'services')
    pairs = conf['pairs'].split(',')
    timeframes = conf['timeframes'].split(',')

    # UTC time
    now = int(time.mktime(datetime.datetime.now().timetuple()))

    for pair in pairs:
        for tf in timeframes:
            try:
                data = internal.import_numpy(pair, tf, 21)
            except:
                print('Failed import ', pair, tf)
                pass

            try:
                response = check_bb(data)
                name = 'BBBREAK'
                if response != False:
                    event = { 'time' : now,
                              'symbol': pair,
                              'timeframe': tf,
                              'type': name,
                              'direction': response
                            }
                    put('http://localhost:5000/events', data={'data': str(event)})
                    put('http://localhost:3000/api/events', data={'data': str(event)})
                response = False
            except:
                print('Failed bb ', pair, tf)
                pass

            try:
                response = check_sma(data)
                name = 'SMACROSS'
                if response != False:
                    event = {'time': now,
                             'symbol': pair,
                             'timeframe': tf,
                             'type': name,
                             'direction': response
                             }
                    put('http://localhost:5000/events', data={'data': str(event)})
                response = False
            except:
                print('Failed sma ', pair, tf)
                pass
            try:
                response = check_dildo(data)
                name = 'DILDO'
                if response != False:
                    event = {'time': now,
                             'symbol': pair,
                             'timeframe': tf,
                             'type': name,
                             'direction': response
                             }
                    put('http://localhost:5000/events', data={'data': str(event)})
            except:
                print('Failed dildo ', pair, tf)
                pass


def run_events():
    m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' START event service'
    print(m)
    logging.info(m)
    while True:
        now = int(time.mktime(datetime.datetime.now().timetuple()))
        if now % (60*30) == 0:
            # Wait to perform queries
            time.sleep(2)

            # check events
            update_events()
            m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' CHECK events'
            logging.info(m)

            # sleep for next 29 minutes
            time.sleep(60*29)

        time.sleep(1)