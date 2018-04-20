# -*- coding: utf-8 -*-
import numpy as np
import time
from requests import post
import datetime
import talib
import logging
import traceback

from core.services import internal


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


def update_events(tf):
    conf = internal.Config('config.ini', 'services')
    pairs = conf['pairs'].split(',')
    url_out = 'http://localhost:3000/api/events'
    url_in = 'http://localhost:5000/events'

    # UTC time
    now = int(time.mktime(datetime.datetime.now().timetuple()))

    for pair in pairs:
        try:
            data = internal.import_numpy(pair, tf, 21)
        except Exception as e:
            m = 'events FAILED import ' + pair + tf
            logging.warning(m)
            logging.error(traceback.format_exc())
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
                #put(url_in, data={str(event)})
                post(url_out, data={str(event)})
            response = False
        except:
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
                #put(url_in, data={str(event)})
                post(url_out, data={str(event)})
            response = False
        except:
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
                #put(url_in, data={str(event)})
                post(url_out, data={str(event)})
        except:
            pass


def run_events():
    m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' START event service'
    print(m)
    logging.info(m)
    while True:
        now = int(time.mktime(datetime.datetime.now().timetuple()))

        # 30m
        if now % (60*30) == 0:
            # Wait to perform queries
            time.sleep(2)
            # check events
            update_events('30m')
            m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' CHECK events 30m'
            logging.info(m)

            #1h
            if now % (60 * 60) == 0:
                # Wait to perform queries
                # check events
                update_events('1h')
                m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' CHECK events 1h'
                logging.info(m)

                # 2h
                if now % (60 * 120) == 0:
                    # Wait to perform queries
                    # check events
                    update_events('2h')
                    m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' CHECK events 2h'
                    logging.info(m)

                    # 3h
                    if now % (60 * 180) == 0:
                        # Wait to perform queries
                        # check events
                        update_events('3h')
                        m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' CHECK events 3h'
                        logging.info(m)

                        # 6h
                        if now % (60*6*60) == 0:
                            # Wait to perform queries
                            # check events
                            update_events('6h')
                            m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' CHECK events 6h'
                            logging.info(m)

                            # 12h
                            if now % (60*12*60) == 0:
                                # Wait to perform queries
                                # check events
                                update_events('12h')
                                m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' CHECK events 12h'
                                logging.info(m)

                                # 24h
                                if now % (60*24*60) == 0:
                                    # Wait to perform queries
                                    # check events
                                    update_events('12h')
                                    m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' CHECK events 12h'
                                    logging.info(m)

                                    # 168h
                                    if now % (60 * 168 * 60) == 0:
                                        # Wait to perform queries
                                        # check events
                                        update_events('168h')
                                        m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' CHECK events 168h'
                                        logging.info(m)

            # sleep for next 28 minutes
            dt = int(time.mktime(datetime.datetime.now().timetuple())) - now
            time.sleep(60*30-dt-60)

        time.sleep(1)