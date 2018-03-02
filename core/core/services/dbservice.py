from influxdb import InfluxDBClient
from datetime import datetime
from threading import Thread
import threading
import time
import datetime
import logging
import traceback
import ast
import websocket
import requests
from core.services import internal


# Database websocket service
class BitfinexPairDbservice():
    def __init__(self, db_name, host, port, pair, timeframes ):
        self.client = InfluxDBClient(host, port, 'root', 'root', db_name)
        self.db = db_name
        self.last1 = 0
        self.last2 =0
        self.pair = pair
        self.client.create_database(db_name)
        self.timeframes = timeframes
        self.i = 0

        # Alter default retention policy
        q = 'ALTER RETENTION POLICY "autogen" ON '+self.db+' DURATION 53w DEFAULT'
        self.client.query(q)

        # Create retention policy for tickers
        self.client.create_retention_policy('tickerdelete', '1h', '1', default=False)

    # Creates Continuous Query with a given timeframe
    def create_conquery(self):
        # Continuous Queries for each par for each period
        # create cq BTCUSD1h on DATABASE begin ... into BTCUSD1h from tBTCUSD group by time(1h) end

        # Continuous queries
        for tf in self.timeframes:
            try:
                query = 'CREATE CONTINUOUS QUERY ' \
                        '' + self.pair + tf + ' ON ' + self.db + ' RESAMPLE EVERY 5m BEGIN SELECT ' \
                                                                                         'first(open) AS open,' \
                                                                                         'max(high) AS high, ' \
                                                                                         'min(low) AS low, ' \
                                                                                         'last(close) AS close, ' \
                                                                                         'sum(volume) AS volume  ' \
                                                                                         'INTO ' + self.pair + tf + ' FROM ' + self.pair + ' GROUP BY time(' + tf + ') END'

                self.client.query(query)
            except Exception as e:
                logging.error(traceback.format_exc())
                pass

    # Writes candlestick from message to InfluxDB
    def write_ticker(self, ticker):

        json_body = [
            {
                "measurement": self.pair,
                "time": int(1000000 * ticker[0]),
                "fields": {
                    "open": float(ticker[1]),
                    "close": float(ticker[2]),
                    "high": float(ticker[3]),
                    "low": float(ticker[4]),
                    "volume": float(ticker[5]),
                }
            }
        ]
        # TODO: retention policy
        status = self.client.write_points(json_body) # retention_policy='tickerdelete')

        return status

    def downsample(self, tf, pair):
        now = "'" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")) + "'"
        try:
            query = 'SELECT first(open) AS open, max(high) AS high, min(low) AS low, last(close) AS close, sum(volume) AS volume ' \
                    'INTO ' + pair + tf + ' FROM ' + pair + ' WHERE time <=' + now + ' GROUP BY time(' + tf + ')'

            self.client.query(query)
        except Exception as e:
            m = str(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")) + 'FAILED downsample' + pair + tf
            logging.WARNING(m)
            logging.error(traceback.format_exc())
            pass

    # Websocket messages handler
    def on_message(self, ws, message):
        # self.i allows to ommit two firs messages from websocket
        if self.i > 1:
            try:
                response = ast.literal_eval(message)[1]
                if response != 'hb':
                    # Dump handling - normal ticker message has 6 values, dump is a longer message
                    if len(response) > 6:
                        for ticker in response:
                            self.write_ticker(ticker)
                        # Down sample data
                        for tf in self.timeframes:
                            self.downsample(tf, self.pair)

                        m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' ' + self.pair + ' dump record saved.'
                        logging.info(m)

                    # Single ticker handling
                    elif response[0] != self.last1 and response[0] != self.last2:
                        try:
                            status = self.write_ticker(response)
                            self.last2 = self.last1
                            self.last1 = response[0]
                        except Exception as e:
                            m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' Ticker write failed ' + str(self.pair)
                            logging.warning(m)
                            logging.error(traceback.format_exc())
                            pass
            except Exception as e:
                logging.error(traceback.format_exc())
                pass
        if self.i < 2:
            self.i += 1

    def on_error(self, ws, error):
        m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' ' + self.pair + ' error occured!'
        logging.warning(m)
        #self.on_open(ws)

    def on_close(self, ws):
        m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' ' + self.pair + ' connection closed.'
        logging.warning(m)
        #self.on_open(ws)

    # Subscribe to new channel
    def on_open(self, ws):
        def run(*args):
            ws.send('{ \
                        "event": "subscribe",\
                        "channel": "candles", \
                        "key": "trade:1m:t' + self.pair + '" \
                    }')
            m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' ' + self.pair + ' connection opened.'
            logging.info(m)

        Thread(target=run).start()

        # resets the value of self.i
        self.i = 0

    # create service
    def create(self):
        # Continuousqueries
        self.create_conquery()
        # Websocket channel
        ws = websocket.WebSocketApp("wss://api.bitfinex.com/ws/2",
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        ws.on_open = self.on_open
        while True:
            ws.run_forever()


def run_dbservice():
    ################### CONFIG ###################

    conf = internal.Config('config.ini', 'services')
    db_name = conf['db_name']
    host = conf['host']
    port = int(conf['port'])

    pairs = conf['pairs'].split(',')
    timeframes = conf['timeframes'].split(',')

    ##############################################

    threads = []
    for pair in pairs:
        service = BitfinexPairDbservice(db_name, host, port, pair, timeframes)
        threads.append(threading.Thread(target=service.create))

    for t in threads:
        t.setDaemon(True)

    for t in threads:
        t.start()
        time.sleep(5)

    m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' START database service'
    print(m)
    logging.info(m)

    while True:
        m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' Active threads: ' + str(threading.active_count()-1)
        print(m)
        logging.info(m)
        time.sleep(60 * 30)


# Database Bitfinex fill
def bitfinex_fill(client, pair, timeframe, limit, t=6):

    try:
        # Map timeframes for Bitfinex
        if timeframe == '24h':
            timeframe = '1D'
        elif timeframe == '168h':
            timeframe = '7D'

        url = 'https://api.bitfinex.com/v2/candles/trade:' + timeframe + ':t' + pair + '/hist?limit=' + str(
            limit) + '&start=946684800000'
        request = requests.get(url)
        candel_list = request.json()

        # Map timeframes for influx
        if timeframe == '1D':
            timeframe = '24h'
        elif timeframe == '7D':
            timeframe = '168h'

        # check if any response and if not error then write candles to influx
        if len(candel_list) > 0:
            if candel_list[0] != 'error':
                try:
                    for i in range(len(candel_list)):
                        try:
                            json_body = [
                                {
                                    "measurement": pair + timeframe,
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
                            m = str(datetime.datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED ticker write'
                            logging.warning(m)
                            logging.error(traceback.format_exc())
                            pass

                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair +' ' + timeframe + ' SUCCEED records: ' + str(len(candel_list))
                    logging.info(m)
                    print(m)
                except Exception as e:
                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED : ' + str(
                        len(candel_list))
                    logging.warning(m)
                    print(m)
                    pass
        else:
            m = str(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED Bitfinex response'
            logging.warning(m)

        if timeframe == '1h':
            for tf in ['2h', '3h', '6h', '12h', '24h', '168h']:
                #IMEFRAME DOWNSAMPLING
                now = "'" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")) + "'"
                try:
                    query = 'SELECT first(open) AS open, max(high) AS high, min(low) AS low, last(close) AS close, sum(volume) AS volume ' \
                            'INTO ' + pair + tf+' FROM ' + pair + '1h WHERE time <=' + now + ' GROUP BY time('+tf+')'

                    client.query(query)
                except Exception as e:
                    m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + 'FAILED '+tf+' downsample' + pair
                    logging.WARNING(m)
                    logging.error(traceback.format_exc())
                    print(m)
                    pass

        status = True

    except Exception as e:
        m = str(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")) + ' ' + pair + timeframe + ' FAILED Bitfinex api request'
        logging.warning(m)
        logging.error(traceback.format_exc())
        status=False

    return status


def bittrex_fill(client, pair, timeframe, limit, t=2):
    name_map = {'30m': 'thirtyMin',
                '1h': 'hour',
                '2h': 'hour',
                '3h': 'hour',
                '6h':'hour',
                '12h':'hour',
                '24h': 'day',
                '168h': 'day',
    }

    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = end_pair + '-' + start_pair

    status = False

    if timeframe == '1h':
        # HOURS
        try:
            url = 'https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=' + req_pair + '&tickInterval=hour'
            request = requests.get(url)
            response = request.json()

            # check if any response and if not error then write candles to influx
            if response['success'] == True:
                candel_list= response['result']
                try:
                    for row in candel_list:
                        try:
                            json_body = [
                                {
                                    "measurement": pair + '1h',
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
                            m = str(datetime.datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' hour FAILED ticker write'
                            logging.warning(m)
                            logging.error(traceback.format_exc())
                            pass

                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair +' hour SUCCEED '
                    logging.info(m)
                    print(m)
                except Exception as e:
                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' hour FAILED ticker write'
                    logging.warning(m)
                    print(m)
                    pass
            else:
                m = str(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' hour FAILED Bitrex response ' + response['message']
                logging.warning(m)

            # Avoid blocked API
            time.sleep(t)
        except Exception as e:
            m = str(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' hour FAILED Bitrex api request'
            logging.warning(m)
            logging.error(traceback.format_exc())

    elif timeframe == '24h':
        # DAYS
        try:
            url = 'https://bittrex.com/Api/v2.0/pub/market/GetTicks?marketName=' + req_pair + '&tickInterval=day'
            request = requests.get(url)
            response = request.json()

            # check if any response and if not error then write candles to influx
            if response['success'] == True:
                candel_list= response['result']
                try:
                    for row in candel_list:
                        try:
                            json_body = [
                                {
                                    "measurement": pair + '24h',
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
                            m = str(datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' day FAILED ticker write'
                            logging.warning(m)
                            logging.error(traceback.format_exc())
                            pass

                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' day SUCCEED'
                    logging.info(m)
                    print(m)
                except Exception as e:
                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' day FAILED ticker write'
                    logging.warning(m)
                    print(m)
                    pass
            else:
                m = str(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' day FAILED Bitrex response ' + response['message']
                logging.warning(m)

            # Avoid blocked API
            time.sleep(t)
        except Exception as e:
            m = str(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' day FAILED Bitrex api request'
            logging.warning(m)
            logging.error(traceback.format_exc())

        # TIMEFRAME DOWNSAMPLING
        timeframes2 = ['2h', '3h', '6h', '12h', '24h', '168h']
        now = "'" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")) + "'"
        for tf in timeframes2:
            try:
                query = 'SELECT first(open) AS open, max(high) AS high, min(low) AS low, last(close) AS close, sum(volume) AS volume ' \
                        'INTO ' + pair + tf + ' FROM ' + pair + '1h WHERE time <=' + now + ' GROUP BY time(' + tf + ')'

                client.query(query)
            except Exception as e:
                m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + 'FAILED ' + tf + ' downsample' + pair
                logging.WARNING(m)
                logging.error(traceback.format_exc())
                print(m)
                pass

        #DOWNSAMPLE 1WEEK
        try:
            query = 'SELECT first(open) AS open, max(high) AS high, min(low) AS low, last(close) AS close, sum(volume) AS volume ' \
                    'INTO ' + pair + '168h FROM ' + pair + '24h WHERE time <=' + now + ' GROUP BY time(168h)'

            client.query(query)
        except Exception as e:
            m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + 'FAILED 168h downsample' + pair
            logging.WARNING(m)
            logging.error(traceback.format_exc())
            print(m)
        pass

    return status


def binance_fill(client, pair, timeframe, limit, t=4):
    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = start_pair + end_pair
    exchange = 'Binance'

    try:
        # Map timeframes for Binance
        if timeframe == '24h':
            timeframe = '1d'
        elif timeframe == '168h':
            timeframe = '1w'
        elif timeframe =='3h':
            timeframe='1h'

        # defualt last 500 candles
        url = 'https://api.binance.com/api/v1/klines?symbol=' + req_pair + '&interval='+ timeframe
        request = requests.get(url)
        candel_list = request.json()

        # Map timeframes for influx
        if timeframe == '1d':
            timeframe = '24h'
        elif timeframe == '1w':
            timeframe = '168h'

        # check if any response and if not error then write candles to influx
        if isinstance(candel_list,list) == True:
            try:
                for i in range(len(candel_list)):
                    try:
                        json_body = [
                            {
                                "measurement": pair + timeframe,
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
                        m = str(datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED ticker write'
                        logging.warning(m)
                        logging.error(traceback.format_exc())
                        pass

                m = str(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' SUCCEED records: ' + str(
                    len(candel_list))
                logging.info(m)
                print(m)
            except Exception as e:
                m = str(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED : ' + str(
                    len(candel_list))
                logging.warning(m)
                print(m)
                pass
        else:
            m = str(datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED {exchange} response'
            logging.warning(m)

    except Exception as e:
        m = str(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")) + ' ' + pair + timeframe + ' FAILED {exchange} api request'
        logging.warning(m)
        logging.error(traceback.format_exc())

    if timeframe == '1h':
        for tf in ['2h', '3h', '6h', '12h', '24h', '168h']:
            # IMEFRAME DOWNSAMPLING
            now = "'" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")) + "'"
            try:
                query = 'SELECT first(open) AS open, max(high) AS high, min(low) AS low, last(close) AS close, sum(volume) AS volume ' \
                        'INTO ' + pair + tf + ' FROM ' + pair + '1h WHERE time <=' + now + ' GROUP BY time(' + tf + ')'

                client.query(query)
            except Exception as e:
                m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + 'FAILED ' + tf + ' downsample' + pair
                logging.WARNING(m)
                logging.error(traceback.format_exc())
                print(m)
                pass


def poloniex_fill(client, pair, timeframe,limit, t=4):
    #Returns candlestick chart data. Required GET parameters are "currencyPair", "period"
    # (candlestick period in seconds; valid values are 300, 900, 1800, 7200, 14400, and 86400),
    # "start", and "end". "Start" and "end" are given in UNIX timestamp format and used to specify
    # the date range for the data returned. Sample output:

    end_pair = pair[-3:]
    start_pair = pair[:-3]
    if end_pair == 'USD':
        end_pair = end_pair + 'T'
    req_pair = end_pair + '_' + start_pair
    exchange = 'Poloniex'


    try:
        # Build 1h
        if timeframe == '1h':
            now = int(time.time())
            url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end={}&period={}'.format(req_pair, now - 6*limit*60*30, now, 1800)
            request = requests.get(url)
            candel_list = request.json()
            # check if any response and if not error then write candles to influx
            if isinstance(candel_list,list) == True:
                try:
                    for i in range(len(candel_list)):
                        try:
                            json_body = [
                                {
                                    "measurement": pair + '30m',
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
                            m = str(datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED ticker write'
                            logging.warning(m)
                            logging.error(traceback.format_exc())
                            pass

                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' SUCCEED records: ' + str(
                        len(candel_list))
                    logging.info(m)
                    print(m)
                except Exception as e:
                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED : ' + str(
                        len(candel_list))
                    logging.warning(m)
                    print(m)
                    pass
            else:
                m = str(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED {} response'.format(exchange)
                logging.warning(m)

            # 1h TIMEFRAME DOWNSAMPLING
            now = "'" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")) + "'"
            try:
                query = 'SELECT first(open) AS open, max(high) AS high, min(low) AS low, last(close) AS close, sum(volume) AS volume ' \
                        'INTO ' + pair + '1h FROM ' + pair + '30m WHERE time <=' + now + ' GROUP BY time(1h)'

                client.query(query)
            except Exception as e:
                m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + 'FAILED 1h downsample' + pair
                logging.WARNING(m)
                logging.error(traceback.format_exc())
                print(m)
                pass

            # TIMEFRAME DOWNSAMPLING
            for tf in ['2h', '3h', '6h', '12h', '24h', '168h']:
                now = "'" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")) + "'"
                try:
                    query = 'SELECT first(open) AS open, max(high) AS high, min(low) AS low, last(close) AS close, sum(volume) AS volume ' \
                            'INTO ' + pair + tf+' FROM ' + pair + '1h WHERE time <=' + now + ' GROUP BY time('+tf+')'
                    client.query(query)
                except Exception as e:
                    m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + 'FAILED '+tf+' downsample' + pair
                    logging.WARNING(m)
                    logging.error(traceback.format_exc())
                    print(m)
                    pass

        elif timeframe == '2h':
            now = time.time()
            url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end=9999999999&period={}'.format(
                req_pair, now - 6*limit*60*60*2, 7200)
            request = requests.get(url)
            candel_list = request.json()

            # check if any response and if not error then write candles to influx
            if isinstance(candel_list,list) == True:
                try:
                    for i in range(len(candel_list)):
                        try:
                            #151598160000000000
                            #1515759780000000000

                            json_body = [
                                {
                                    "measurement": pair + '2h',
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
                            m = str(datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED ticker write'
                            logging.warning(m)
                            logging.error(traceback.format_exc())
                            pass

                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' SUCCEED records: ' + str(
                        len(candel_list))
                    logging.info(m)
                    print(m)
                except Exception as e:
                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED : ' + str(
                        len(candel_list))
                    logging.warning(m)
                    print(m)
                    pass
            else:
                m = str(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED {} response'.format(exchange)
                logging.warning(m)

            # 6h TIMEFRAME DOWNSAMPLING
            now = "'" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")) + "'"
            try:
                query = 'SELECT first(open) AS open, max(high) AS high, min(low) AS low, last(close) AS close, sum(volume) AS volume ' \
                        'INTO ' + pair + '6h FROM ' + pair + '2h WHERE time <=' + now + ' GROUP BY time(6h)'

                client.query(query)
            except Exception as e:
                m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + 'FAILED 2h downsample' + pair
                logging.WARNING(m)
                logging.error(traceback.format_exc())
                print(m)
                pass

            # 12h TIMEFRAME DOWNSAMPLING
            now = "'" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")) + "'"
            try:
                query = 'SELECT first(open) AS open, max(high) AS high, min(low) AS low, last(close) AS close, sum(volume) AS volume ' \
                        'INTO ' + pair + '12h FROM ' + pair + '2m WHERE time <=' + now + ' GROUP BY time(12h)'

                client.query(query)
            except Exception as e:
                m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + 'FAILED 12h downsample' + pair
                logging.WARNING(m)
                logging.error(traceback.format_exc())
                print(m)
                pass
        elif timeframe == '24h':
            now = time.time()
            url = 'https://poloniex.com/public?command=returnChartData&currencyPair={}&start={}&end=9999999999&period={}'.format(
                req_pair, now - 7 * limit * 60 * 60 * 24, 86400)
            request = requests.get(url)
            candel_list = request.json()

            # check if any response and if not error then write candles to influx
            if isinstance(candel_list, list) == True:
                try:
                    for i in range(len(candel_list)):
                        try:
                            json_body = [
                                {
                                    "measurement": pair + '24h',
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
                            m = str(datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED ticker write'
                            logging.warning(m)
                            logging.error(traceback.format_exc())
                            pass

                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' SUCCEED records: ' + str(
                        len(candel_list))
                    logging.info(m)
                    print(m)
                except Exception as e:
                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED : ' + str(
                        len(candel_list))
                    logging.warning(m)
                    print(m)
                    pass
            else:
                m = str(datetime.datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' FAILED {} response'.format(exchange)
                logging.warning(m)

            # 168h TIMEFRAME DOWNSAMPLING
            now = "'" + str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")) + "'"
            try:
                query = 'SELECT first(open) AS open, max(high) AS high, min(low) AS low, last(close) AS close, sum(volume) AS volume ' \
                        'INTO ' + pair + '168h FROM ' + pair + '24h WHERE time <=' + now + ' GROUP BY time(168h)'

                client.query(query)
            except Exception as e:
                m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + 'FAILED 168h downsample' + pair
                logging.WARNING(m)
                logging.error(traceback.format_exc())
                print(m)
                pass

    except Exception as e:
        m = str(datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S")) + ' ' + pair + timeframe + ' FAILED {} api request'.format(exchange)
        logging.warning(m)
        logging.error(traceback.format_exc())


def pair_fill(pair, exchange, last):
    conf = internal.Config('config.ini', 'services')
    db_name = conf['db_name']
    host = conf['host']
    port = int(conf['port'])
    client = InfluxDBClient(host, port, 'root', 'root', db_name)

    h_number = int((int(time.time()) - last)/3600)+1
    threshold = 169

    if exchange == 'bitfinex':
        if h_number <= threshold:
            timeframes = ['1h']
            t = 0
        else:
            timeframes = ['1h', '3h', '6h', '12h', '24h', '168h']
            t = 2

        fill_type = exchange + '_fill'
        for tf in timeframes:
            limit = min(int(h_number / int(tf[:-1])) + 2, 700)
            filler = globals()[fill_type]
            filler(client, pair, tf, limit, t)

    elif exchange == 'bittrex':
        if h_number <= threshold:
            timeframes = ['1h']
        else:
            timeframes = ['1h', '24h']

        fill_type = exchange+'_fill'
        for tf in timeframes:
            limit = int(h_number/int(tf[:-1]))+2
            filler = globals()[fill_type]
            filler(client, pair, tf, limit, t=0)

    elif exchange == 'binance':
        if h_number <= threshold:
            timeframes = ['1h']
            t=0
        else:
            timeframes = ['1h', '2h', '6h', '12h', '24h', '168h']
            t = 1

        fill_type = exchange + '_fill'
        for tf in timeframes:
            limit = int(h_number / int(tf[:-1])) + 2
            filler = globals()[fill_type]
            filler(client, pair, tf, limit, t)

    elif exchange == 'poloniex':
        if h_number <= threshold:
            timeframes = ['1h']
        else:
            timeframes = ['1h', '2h', '24h']

        fill_type = exchange + '_fill'
        for tf in timeframes:
            limit = int(h_number / int(tf[:-1])) + 2
            filler = globals()[fill_type]
            filler(client, pair, tf, limit, t=0)





