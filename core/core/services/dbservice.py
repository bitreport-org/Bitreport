from influxdb import InfluxDBClient
from datetime import datetime as dt
import time
import logging
import traceback
import requests
from core.services import internal


# Database Bitfinex fill
logtime = dt.now().strftime("%Y-%m-%d %H:%M:%S")

def bitfinex_fill(client, pair, timeframe, limit):

    try:
        # Map timeframes for Bitfinex
        timeframeR = timeframe
        if timeframe == '24h':
            timeframeR = '1D'
        elif timeframe == '168h':
            timeframeR = '7D'
        elif timeframe == '2h':
            timeframeR = '1h'

        url = 'https://api.bitfinex.com/v2/candles/trade:{}:t{}/hist?limit={}&start=946684800000'.format(timeframeR, pair, limit)
        request = requests.get(url)
        candel_list = request.json()


        # check if any response and if not error then write candles to influx
        l = len(candel_list)
        name = pair+timeframe

        if l > 0 and candel_list[0] != 'error':
            try:
                for i in range(l):
                    try:
                        json_body = [
                            {
                                "measurement": name,
                                "time": int(1000000 * candel_list[i][0]),
                                "fields": {
                                    "open": float(candel_list[i][1]),
                                    "close": float(candel_list[i][2]),
                                    "high": float(candel_list[i][3]),
                                    "low": float(candel_list[i][4]),
                                    "volume": float(candel_list[i][5]),
                                }
                            }
                        ]
                        client.write_points(json_body)
                    except Exception as e:
                        m = '{} FAILED ticker write {}'.format(logtime, name)
                        logging.warning(m)
                        logging.error(traceback.format_exc())
                        pass

                m = '{} SUCCEDED write {} records for {}'.format(logtime, l, name)
                logging.warning(m)
                print(m)
            except Exception as e:
                m = '{} FAILED write {}'.format(logtime, name)
                logging.warning(m)
                print(m)
                pass
        else:
            m = '{} FAILED {} Bitfinex response'.format(logtime, name)
            logging.warning(m)

        if timeframeR == '1h':
            for tf in ['2h']:
                #TIMEFRAME DOWNSAMPLING
                try:

                    query = "SELECT " \
                            "first(open) AS open, " \
                            "max(high) AS high, " \
                            "min(low) AS low, " \
                            "last(close) AS close, " \
                            "sum(volume) AS volume " \
                            "INTO {} FROM {}1h WHERE time <= '{}' GROUP BY time({})".format(pair+tf, pair, logtime, tf)
                    client.query(query)
                except Exception as e:
                    m = '{} FAILED {} downsample {}'.format(logtime, tf, pair)
                    logging.warning(m)
                    logging.error(traceback.format_exc())
                    print(m)
                    pass

        status = True

    except Exception as e:
        m = '{} FAILED Bitfinex api request for {}'.format(logtime, name)
        logging.warning(m)
        logging.error(traceback.format_exc())
        status = False

    return status


def bittrex_fill(client, pair, timeframe, limit):
    name_map = {'30m': 'thirtyMin',
                '1h': 'hour',
                '2h': 'hour',
                '3h': 'hour',
                '6h':'hour',
                '12h':'hour',
                '24h': 'day',
                '168h': 'day',
                'hour' : '1h',
                'day' : '24h',
                'thirtyMin' : '30m'
    }
    downsamples = {
        'hour': ['2h', '3h', '6h', '12h'],
        'day': ['168h'],
        'thirtyMin': []
    }
    name = pair+timeframe
    status = False

    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = end_pair + '-' + start_pair

    interval = name_map[timeframe]
    measurement_name = name_map[interval]

    try:
        url = 'https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName={}&tickInterval={}'.format(req_pair, interval)
        request = requests.get(url)
        response = request.json()

        # check if any response and if not error then write candles to influx
        if response['success']:
            candel_list = response['result']
            try:
                # Write ticker
                for row in candel_list:
                    try:
                        json_body = [
                            {
                                "measurement": measurement_name,
                                "time": row['T'],
                                "fields": {
                                    "open": float(row['O']),
                                    "close": float(row['C']),
                                    "high": float(row['H']),
                                    "low": float(row['L']),
                                    "volume": float(row['BV']),
                                }
                            }
                        ]
                        client.write_points(json_body)
                    except Exception as e:
                        m = '{} FAILED ticker write {}'.format(logtime, name)
                        logging.warning(m)
                        logging.error(traceback.format_exc())
                    pass
                m = '{} SUCCEDED write records for {}'.format(logtime, name)
                logging.warning(m)
                print(m)

                # Data downsample
                timeframes2 = downsamples[measurement_name]
                for tf in timeframes2:
                    try:
                        query = "SELECT first(open) AS open, " \
                                "max(high) AS high," \
                                "min(low) AS low, " \
                                "last(close) AS close, " \
                                "sum(volume) AS volume " \
                                "INTO {} FROM {} WHERE time <= '{}' GROUP BY time({})".format(name, pair + measurement_name, logtime, tf)

                        client.query(query)
                    except Exception as e:
                        m = '{} FAILED {} downsample {}'.format(logtime, tf, pair)
                        logging.warning(m)
                        logging.error(traceback.format_exc())
                        print(m)
                        pass

            except Exception as e:
                m = '{} FAILED write {}'.format(logtime, name)
                logging.warning(m)
                print(m)
                pass
        else:
            m = '{} FAILED {} Bitrex response: {}'.format(logtime, name, response['message'])
            logging.warning(m)
    except Exception as e:
        m = '{} FAILED Bitrex api request for {}'.format(logtime, name)
        logging.warning(m)

    return status


def binance_fill(client, pair, timeframe, limit):
    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = start_pair + end_pair
    name = pair+timeframe
    status = False

    try:
        timeframeR=timeframe
        # Map timeframes for Binance
        if timeframe == '24h':
            timeframeR = '1d'
        elif timeframe == '168h':
            timeframeR = '1w'

        # defualt last 500 candles
        url = 'https://api.binance.com/api/v1/klines?symbol={}&interval={}'.format(req_pair, timeframeR)
        request = requests.get(url)
        candel_list = request.json()

        # check if any response and if not error then write candles to influx
        if isinstance(candel_list,list) == True:
            try:
                l = len(candel_list)
                for i in range(l):
                    try:
                        json_body = [
                            {
                                "measurement": name,
                                "time": int(1000000 * candel_list[i][0]),
                                "fields": {
                                    "open": float(candel_list[i][1]),
                                    "close": float(candel_list[i][4]),
                                    "high": float(candel_list[i][2]),
                                    "low": float(candel_list[i][3]),
                                    "volume": float(candel_list[i][5]),
                                }
                            }
                        ]
                        client.write_points(json_body)
                    except Exception as e:
                        m = '{} FAILED ticker write {}'.format(logtime, name)
                        logging.warning(m)
                        logging.error(traceback.format_exc())
                        pass

                status = True
                m = '{} SUCCEDED write {} records for {}'.format(logtime, l, name)
                logging.warning(m)
                print(m)

            except Exception as e:
                m = '{} FAILED write {}'.format(logtime, name)
                logging.warning(m)
                print(m)
                pass

            # Downsampling
            if timeframeR == '1h':
                for tf in ['3h']:
                    try:
                        query = "SELECT " \
                                "first(open) AS open, " \
                                "max(high) AS high, " \
                                "min(low) AS low, " \
                                "last(close) AS close, " \
                                "sum(volume) AS volume " \
                                "INTO {} FROM {}1h WHERE time <= '{}' GROUP BY time({})".format(pair + tf,
                                                                                                  pair, logtime, tf)
                        client.query(query)
                    except Exception as e:
                        m = '{} FAILED {} downsample {}'.format(logtime, tf, pair)
                        logging.warning(m)
                        logging.error(traceback.format_exc())
                        print(m)
                        pass
        else:
            m = '{} FAILED {} Binance response'.format(logtime, name)
            logging.warning(m)


    except Exception as e:
        m = '{} FAILED Binance api request for {}'.format(logtime, name)
        logging.warning(m)
        logging.error(traceback.format_exc())
        pass

    return status


def poloniex_fill(client, pair, timeframe,limit):
    #Returns candlestick chart data. Required GET parameters are "currencyPair", "period"
    # (candlestick period in seconds; valid values are 300, 900, 1800, 7200, 14400, and 86400),
    # "start", and "end". "Start" and "end" are given in UNIX timestamp format and used to specify
    # the date range for the data returned. Sample output:
    status = False
    now = int(time.time())
    request_types = {
        '30m': {'name': '30m', 'start': now - 6 * limit * 60 * 30, 'downsamples': ['1h', '3h'], 'value': 1800},
        '2h': {'name': '2h', 'start': now - 6 * limit * 60 * 60 * 2, 'downsaples': ['6h', '12h'], 'value': 7200},
        '24h': {'name': '24h', 'start': now - 7 * limit * 60 * 60 * 24, 'downsaples': ['168h'], 'value': 86400}
    }
    name_map = {'30m': '30m',
                '1h': '30m',
                '2h': '2h',
                '3h': '30m',
                '6h': '2h',
                '12h': '2h',
                '24h': '24h',
                '168h': '24h',
                }

    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = end_pair + '_' + start_pair
    name = pair + timeframe

    try:
        r = request_types[name_map[timeframe]]
        url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'.format(req_pair, r['start'], now, r['value'])
        request = requests.get(url)
        candel_list = request.json()
        # check if any response and if not error then write candles to influx
        if isinstance(candel_list, list):
            try:
                l = len(candel_list)
                for i in range(l):
                    try:
                        json_body = [
                            {
                                "measurement": pair + r['name'],
                                "time": int(1000000000 * candel_list[i]['date']),
                                "fields": {
                                    "open": float(candel_list[i]['open']),
                                    "close": float(candel_list[i]['close']),
                                    "high": float(candel_list[i]['high']),
                                    "low": float(candel_list[i]['low']),
                                    "volume": float(candel_list[i]['volume']),
                                }
                            }
                        ]
                        client.write_points(json_body)
                    except Exception as e:
                        m = '{} FAILED ticker write {}'.format(logtime, name)
                        logging.warning(m)
                        logging.error(traceback.format_exc())
                        pass
                status = True
                m = '{} SUCCEDED write {} records for {}'.format(logtime, l, name)
                logging.warning(m)
                print(m)

                # Downsampling
                for tf in r['downsamples']:
                    # 1h TIMEFRAME DOWNSAMPLING
                    try:
                        query = "SELECT first(open) AS open, " \
                                "max(high) AS high, " \
                                "min(low) AS low, " \
                                "last(close) AS close, " \
                                "sum(volume) AS volume " \
                                "INTO {} FROM {} WHERE time <= '{}' GROUP BY time({})" .format(pair+tf, pair+r['name'], logtime, tf)
                        client.query(query)
                    except Exception as e:
                        m = '{} FAILED {} downsample {}'.format(logtime, tf, pair)
                        logging.warning(m)
                        logging.error(traceback.format_exc())
                        print(m)
                        pass

            except Exception as e:
                m = '{} FAILED write {}'.format(logtime, name)
                logging.warning(m)
                print(m)
                pass
        else:
            m = '{} FAILED {} Poloniex response'.format(logtime, name)
            logging.warning(m)
    except Exception as e:
        m = '{} FAILED Poloniex api request for {}'.format(logtime, name)
        logging.warning(m)
        logging.error(traceback.format_exc())
        status = False

    return status

def pair_fill(pair, exchange, last):
    tic = time.time()

    conf = internal.Config('config.ini', 'services')
    db_name = conf['db_name']
    host = conf['host']
    port = int(conf['port'])
    client = InfluxDBClient(host, port, 'root', 'root', db_name)

    if last == None:
        last = internal.import_numpy(pair, '1h', 1)

    if not last:
        h_number = 168*52
    else:
        h_number = int((time.time() - last['date'][0] / 3600))+2


    if exchange == 'bitfinex':
        timeframes = ['1h', '3h', '6h', '12h', '24h', '168h']
        fill_type = exchange + '_fill'
        filler = globals()[fill_type]

        for tf in timeframes:
            limit = min(int(h_number / int(tf[:-1])) + 2, 700)

            start = time.time()
            filler(client, pair, tf, limit)
            dt = time.time() - start
            time.sleep(max(0, 2-dt))

    elif exchange == 'bittrex':
        timeframes = ['1h', '24h']

        fill_type = exchange+'_fill'
        filler = globals()[fill_type]

        for tf in timeframes:
            limit = int(h_number/int(tf[:-1]))+2
            filler(client, pair, tf, limit)

    elif exchange == 'binance':

        timeframes = ['1h', '2h', '6h', '12h', '24h', '168h']

        fill_type = exchange + '_fill'
        filler = globals()[fill_type]

        for tf in timeframes:
            limit = int(h_number / int(tf[:-1])) + 2

            start = time.time()
            filler(client, pair, tf, limit)
            dt = time.time() - start
            time.sleep(max(0, 2 - dt))

    elif exchange == 'poloniex':

        timeframes = ['1h', '2h', '24h']

        fill_type = exchange + '_fill'
        filler = globals()[fill_type]

        for tf in timeframes:
            limit = int(h_number / int(tf[:-1])) + 2
            start = time.time()

            filler(client, pair, tf, limit)
            dt = time.time() - start
            time.sleep(max(0, 1 - dt))

    toc = time.time()
    m = '{} from {} fill time: {:.2f} ms'.format(pair, exchange, (toc-tic)*1000)
    logging.warning(m)
    print(m)
