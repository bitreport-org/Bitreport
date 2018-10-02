# -*- coding: utf-8 -*-
import time
import traceback
import requests
import config

from influxdb import InfluxDBClient
from datetime import datetime as dt
from core.services import internal

time_now = dt.now().strftime("%Y-%m-%dT%H:%M:%SZ")

def bitfinex_fill(app, client, pair: str, force: bool = False):
    status = False

    timeframes = ['1h', '3h', '6h', '12h', '24h', '168h']
    tf_distance = [3600, 3*3600, 6*3600, 12*3600, 24*3600, 168*3600 ]

    for timeframe, dist in zip(timeframes, tf_distance):
        # Check last available record
        if force:
            limit = 600
        else:
            try:
                startTime = internal.import_numpy(pair, timeframe, 1)
                startTime = startTime['date'][0]-1
                now = int(time.time())
                limit = int(min((now - startTime) / dist + 1, 600))
            except:
                limit = min(3600 * 24 * 30 * 6, 600)
                pass

        if limit >= 1:
            name = pair + timeframe
            # Map timeframes for Bitfinex
            timeframeR = timeframe
            if timeframe == '24h':
                timeframeR = '1D'
            elif timeframe == '168h':
                timeframeR = '7D'

            url = 'https://api.bitfinex.com/v2/candles/trade:{}:t{}/hist?limit={}'.format(timeframeR, pair, limit)
            request = requests.get(url)
            response = request.json()

            if isinstance(response, list) and response[0] != 'error':
                count = 0 
                points = []
                for row in response:  
                    json_body = {
                                "measurement": name,
                                "time": int(1000000 * row[0]),
                                "fields": {
                                    "open": float(row[1]),
                                    "close": float(row[2]),
                                    "high": float(row[3]),
                                    "low": float(row[4]),
                                    "volume": float(row[5]),
                                }
                            }
                    points.append(json_body)
                    count += 1
                try:
                    client.write_points(points)
                    m = 'SUCCEDED write {} / {} records for {}'.format(count, len(response), name)
                    app.logger.info(m)
                    status = True
                except:
                    m = 'FAILED to write records for {}'.format(name)
                    app.logger.warning(m)
                    return False

                if timeframeR == '1h':
                    tf = '2h'
                    #TIMEFRAME DOWNSAMPLING
                    try:
                        query = "SELECT " \
                                "first(open) AS open, " \
                                "max(high) AS high, " \
                                "min(low) AS low, " \
                                "last(close) AS close, " \
                                "sum(volume) AS volume " \
                                "INTO {} FROM {}1h WHERE time <= '{}' GROUP BY time({})".format(pair+tf, pair, time_now,  tf)
                        client.query(query)
                    except:
                        m = 'FAILED {} downsample {} error: \n {}'.format(tf, pair, traceback.format_exc())
                        app.logger.warning(m)
                        pass

            else:
                m = 'FAILED {} Bitfinex response: {}'.format(name, response[-1])
                app.logger.warning(m)
                status = False
        else:
            app.logger.warning('Data is up to date for {}'.format(pair))
            status = False

    return status


def bittrex_fill(app, client, pair: str, force: bool = False):
    status = False
    downsamples = {
        '1h': ['2h', '3h', '6h', '12h'],
        '24h': ['168h']
    }
    
    # Prepare pair for request
    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = end_pair + '-' + start_pair

    timeframes = ['1h', '24h']
    bittrex_tf = ['hour', 'day']
    for tf, btf in zip(timeframes, bittrex_tf):
        name = pair + tf
        try:
            url = 'https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName={}&tickInterval={}'.format(req_pair, btf)
            request = requests.get(url)
            response = request.json()

            # check if any response and if not error then write candles to influx
            if response.get('success', False):
                candle_list = response.get('result', [])
                if candle_list != []:
                    count = 0 
                    points = []
                    for row in candle_list:
                        json_body = {
                                    "measurement": name,
                                    "time": row['T'],
                                    "fields": {
                                        "open": float(row['O']),
                                        "close": float(row['C']),
                                        "high": float(row['H']),
                                        "low": float(row['L']),
                                        "volume": float(row['BV']),
                                    }
                                }
                        points.append(json_body)
                        count +=1
                    try:
                        client.write_points(points)
                        m = 'SUCCEDED write {} / {} records for {}'.format(count, len(candle_list), name)
                        app.logger.info(m)
                        status = True
                    except:
                        m = 'FAILED to write records for {}'.format(name)
                        app.logger.warning(m)
                        return False

                    # Data downsample
                    for tf_sample in downsamples.get(tf):
                        try:
                            query = "SELECT first(open) AS open, " \
                                    "max(high) AS high," \
                                    "min(low) AS low, " \
                                    "last(close) AS close, " \
                                    "sum(volume) AS volume " \
                                    "INTO {} FROM {} WHERE time <= '{}' GROUP BY time({})".format(pair+tf_sample, name, time_now,  tf_sample)
                            client.query(query)

                        except:
                            m = 'FAILED {} downsample {} error: \n {}'.format( tf, pair, traceback.format_exc())
                            app.logger.warning(m)
                            pass
                else:
                    m = 'FAILED write {}'.format(name)
                    app.logger.warning(m)
                    pass

            else:
                m = 'FAILED {} Bitrex response: {}'.format(name, response.get('message','no message'))
                app.logger.warning(m)

        except:
            m = 'FAILED Bitrex api request for {}'.format(name)
            app.logger.warning(m)
            status = False

    return status


def binance_fill(app, client, pair: str, force: bool = False):
    status = False
    timeframes = ['1h', '2h', '6h', '12h', '24h', '168h']
    tf_distance = [3600, 2*3600, 6*3600, 12*3600, 24*3600, 168*3600 ]

    for timeframe, dist in zip(timeframes, tf_distance):
        # Check last available record
        if force:
            limit = 600
        else:
            try:
                startTime = internal.import_numpy(pair, timeframe, 1)
                startTime = startTime['date'][0] - 1
                now = int(time.time())
                limit = min((now - startTime) / dist + 1, 600)
            except:
                limit = min(3600 * 24 * 30 * 6, 600)
                pass

        if limit >= 1.0:
            #Prepare pair for requests
            end_pair = pair[-3:]
            start_pair = pair[:-3]
            if end_pair == 'USD':
                end_pair = end_pair + 'T'
            req_pair = start_pair + end_pair
            name = pair+timeframe

            # Map timeframes for Binance
            timeframeR = timeframe
            if timeframe == '24h':
                timeframeR = '1d'
            elif timeframe == '168h':
                timeframeR = '1w'

            # max last 500 candles
            url = 'https://api.binance.com/api/v1/klines?symbol={}&interval={}&limit={}'.format(req_pair, timeframeR, min(int(limit)+1, 500))
            request = requests.get(url)
            response = request.json()

            # check if any response and if not error then write candles to influx
            if isinstance(response,list):
                count = 0
                points = []
                for row in response:
                    json_body = {
                                "measurement": name,
                                "time": int(1000000 * row[0]),
                                "fields": {
                                    "open": float(row[1]),
                                    "close": float(row[4]),
                                    "high": float(row[2]),
                                    "low": float(row[3]),
                                    "volume": float(row[5]),
                                }
                            }
                    points.append(json_body)
                    count += 1
                try:
                    client.write_points(points, retention_policy = 'autogen')
                    m = 'SUCCEDED write {} / {} records for {}'.format(count, len(response), name)
                    app.logger.info(m)
                    status = True
                    
                except:
                    m = 'FAILED to write records for {}'.format(name)
                    app.logger.warning(m)
                    return False

                # Downsampling
                if timeframe == '1h':
                    tf = '3h'
                    try:
                        query = "SELECT " \
                                "first(open) AS open, " \
                                "max(high) AS high, " \
                                "min(low) AS low, " \
                                "last(close) AS close, " \
                                "sum(volume) AS volume " \
                                "INTO {} FROM {}1h WHERE time <= '{}' GROUP BY time({})".format(pair + tf, pair, time_now,  tf)
                        client.query(query)
                    except:
                        m = 'FAILED {} downsample {} error: \n {}'.format( tf, pair, traceback.format_exc())
                        app.logger.warning(m)
                        pass
            else:
                m = 'FAILED {} Binance response: {}'.format(name, response.get('msg', 'no error'))
                app.logger.warning(m)

    return status


def poloniex_fill(app, client, pair: str, force: bool = False):
    #Returns candlestick chart data. Required GET parameters are "currencyPair", "period"
    # (candlestick period in seconds; valid values are 300, 900, 1800, 7200, 14400, and 86400),
    # "start", and "end". "Start" and "end" are given in UNIX timestamp format and used to specify
    # the date range for the data returned. Sample output:
    status = False
    now = int(time.time())
    request_types = {
        '30m': {'downsamples': ['1h', '3h'], 'value': 1800},
        '2h': { 'downsamples': ['6h', '12h'], 'value': 7200},
        '24h': {'downsamples': ['168h'], 'value': 86400}
    }

    timeframes = ['30m', '2h', '24h']
    tf_distance = [1800, 2*3600, 24*3600]

    for timeframe, dist in zip(timeframes, tf_distance):
        # Check last available record
        if force:
            limit =3600 * 24 * 30 * 6
            startTime = int(time.time() - limit) - 1
        else:
            try:
                startTime = internal.import_numpy(pair, timeframe, 1)
                startTime = startTime['date'][0] - 1
                now = int(time.time())
                limit = int(min((now - startTime) / dist + 1, 600))
            except:
                limit =3600 * 24 * 30 * 3
                startTime = int(time.time() - limit) - 1
                pass

        if limit >= 1:
            # Prepare pair for request
            end_pair = pair[-3:]
            start_pair = pair[:-3]
            if end_pair == 'USD':
                end_pair = end_pair + 'T'
            req_pair = end_pair + '_' + start_pair
            name = pair + timeframe

            r = request_types.get(timeframe)
            url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&period={}'.format(req_pair, startTime, r['value'])
            request = requests.get(url)
            response = request.json()
            # check if any response and if not error then write candles to influx
            if isinstance(response, list):
                count = 0
                points = []
                for row in response:
                    json_body = {
                                "measurement": pair + timeframe,
                                "time": int(1000000000 * row['date']),
                                "fields": {
                                    "open": float(row['open']),
                                    "close": float(row['close']),
                                    "high": float(row['high']),
                                    "low": float(row['low']),
                                    "volume": float(row['volume']),
                                }
                            }
                    points.append(json_body)
                    count += 1
                try:
                    client.write_points(points)
                    m = 'SUCCEDED write {} / {} records for {}'.format(count, len(response), name)
                    app.logger.info(m)
                    status = True
                except:
                    m = 'FAILED to write records for {}'.format(name)
                    app.logger.warning(m)
                    return False

                # Downsampling
                for tf in r.get('downsamples'):
                    try:
                        query = "SELECT first(open) AS open, " \
                                "max(high) AS high, " \
                                "min(low) AS low, " \
                                "last(close) AS close, " \
                                "sum(volume) AS volume " \
                                "INTO {} FROM {} WHERE time <= '{}' GROUP BY time({})" .format(pair+tf, pair+timeframe, time_now,  tf)
                        client.query(query)
                    except:
                        m = 'FAILED {} downsample {} error: \n {}'.format( tf, pair, traceback.format_exc())
                        app.logger.warning(m)
                        pass
            else:
                m = 'FAILED {} Poloniex response: {}'.format(name, response.get('error', 'no error'))
                app.logger.warning(m)
                status = False

    return status


def pair_fill(app, pair, exchange, force):
    tic = time.time()
    conf = config.BaseConfig()
    result = False

    # connect database
    client = InfluxDBClient(conf.HOST, conf.PORT, 'root', 'root', conf.DBNAME)

    # Fillers
    fillers = dict(
            bitfinex = bitfinex_fill,
            bittrex = bittrex_fill,
            binance = binance_fill,
            poloniex = poloniex_fill
            )
            
    filler = fillers.get(exchange, False)

    # Check if filler exists
    if not filler:
        m = '{} exchange does not exist'.format(exchange)
        app.logger.warning(m)
        return 'Failed', 500

    # Fill database
    result = filler(app, client, pair, force)
        
    if result:
        toc = time.time()
        m = '{} filled from {} fill time: {:.2f} ms'.format( pair, exchange, (toc-tic)*1000)
        app.logger.info(m)
        return 'Success', 200

    else:
        return 'Pair not filled.', 500


def check_exchange(pair: str):
    history = []
    #Bitfinex
    url = 'https://api.bitfinex.com/v2/candles/trade:{}:t{}/hist?limit={}'.format('1D', pair, 1000)
    request = requests.get(url)
    response = request.json()
    if isinstance(response, list) and response != []:
        history.append(('bitfinex', len(response)))

    # bitrex
    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = end_pair + '-' + start_pair
    url = 'https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName={}&tickInterval=24h'.format(req_pair)
    request = requests.get(url)
    response = request.json()
    if response.get('success', False):
        candle_list = response.get('result', None)
        if candle_list:
            history.append(('bittrex', len(candle_list)))

    
    # binance
    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = start_pair + end_pair
    url = 'https://api.binance.com/api/v1/klines?symbol={}&interval={}&limit={}'.format(req_pair, '1d', 500)
    request = requests.get(url)
    response = request.json()
    if isinstance(response,list):
        history.append(('binance', len(response)))
    
    # poloniex
    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = end_pair + '_' + start_pair
    url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start=339361693&end=9999999999&period=86400'.format(req_pair)
    request = requests.get(url)
    response = request.json()
    if isinstance(response, list):
         history.append(('poloniex', len(response)))
    
    history.sort(key=lambda x: x[1])

    if len(history) > 0:
        return history[-1][0]
    else:
        None