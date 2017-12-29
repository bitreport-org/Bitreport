from influxdb import InfluxDBClient
from datetime import datetime
from threading import Thread
import threading
import time
import datetime
import logging
import ast
import websocket
from services import internal

# Database websocket service
class bitfinex_pair_dbservice():
    def __init__(self, db_name, host, port, pair, timeframes ):
        self.client = InfluxDBClient(host, port, 'root', 'root', db_name)
        self.db = db_name
        self.last1 = 0
        self.last2 =0
        self.pair = pair
        self.client.create_database(db_name)
        self.timeframes = timeframes

        logging.basicConfig(filename='logbook.log',format='%(levelname)s:%(message)s', level=logging.INFO)

        # Create retention policy
        # self.client.create_retention_policy('ticker_delete', '1h', '1', default=False)

    # Creates Continuous Query with a given timeframe
    def create_conquery(self):
        # Continuous Queries for each par for each period
        # create cq BTCUSD1h on DATABASE begin ... into BTCUSD1h from tBTCUSD group by time(1h) end

        # Continuous queries
        for tf in self.timeframes:
            try:
                query = 'CREATE CONTINUOUS QUERY ' + self.pair + tf + ' ON ' + self.db + ' RESAMPLE EVERY 5m BEGIN SELECT  \
                                   first(open) AS open, \
                                   max(high) AS high, \
                                   min(low) AS low, \
                                   last(close) AS close, \
                                   sum(volume) AS volume  \
                                   INTO ' + self.pair + tf + ' FROM ' + self.pair + ' GROUP BY time(' + tf + ') END'

                self.client.query(query)
            except:
                print('CQs',tf,'already exists')
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
        status = self.client.write_points(json_body) #retention_policy = 'testrp')

        return status

    # Websocket messages handler
    def on_message(self, ws, message):
        try:
            response = ast.literal_eval(message)[1]
            if response != 'hb':
                # Dump handling - normal ticker message has 6 values, dump is a longer message
                if len(response) > 6:
                    for ticker in response:
                        self.write_ticker(ticker)
                    m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' ' + self.pair + ' dump record saved.'
                    logging.info(m)

                # Single ticker handling
                elif response[0] != self.last1 and response[0] != self.last2:
                    try:
                        status = self.write_ticker(response)
                        self.last2 = self.last1
                        self.last1 = response[0]
                    except:
                        m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' Ticker write failed ' + str(self.pair)
                        logging.warning(m)
                        pass
        except:
            pass

    def on_error(self, ws, error):
        m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' ' + self.pair + ' error occured!'
        logging.warning(m)

        self.on_open(ws)

    def on_close(self, ws):
        m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' ' + self.pair + ' connection closed.'
        logging.warning(m)
        self.on_open(ws)

    # Subscribe to new channel
    def on_open(self, ws):
        def run(*args):
            ws.send('{ \
                        "event": "subscribe",\
                        "channel": "candles", \
                        "key": "trade:1m:t' + self.pair +'" \
                    }')
            m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' ' + self.pair + ' connection opened.'
            logging.info(m)

        Thread(target=run).start()

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
        service = bitfinex_pair_dbservice(db_name, host, port, pair, timeframes)
        threads.append(threading.Thread(target=service.create))

    for t in threads:
        t.setDaemon(True)

    for t in threads:
        t.start()

    m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' START database service'
    print(m)
    logging.info(m)

    while True:
        m = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + ' Active threads: ' + str(threading.active_count()-1)
        print(m)
        logging.info(m)
        time.sleep(60 * 60)


# Database Bitfinex fill
def bitfinex_fill(client, pair, timeframes, limit):
    for timeframe in timeframes:
        url = 'https://api.bitfinex.com/v2/candles/trade:' + timeframe + ':t' + pair + '/hist?limit=' + str(
            limit) + '&start=946684800000'
        request = requests.get(url)
        candel_list = request.json()

        # Map timeframes for influx
        if timeframe == '1D':
            timeframe = '24h'
        elif timeframe == '14D':
            timeframe = '168h'

        # check if any response and if not error then write candles to influx
        if len(candel_list)>0:
            if candel_list[0] != 'error':
                try:
                    for i in range(len(candel_list)):
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
                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair +' ' + timeframe + ' filled successfully. Records: ' + str(len(candel_list))
                    logging.info(m)
                    print(m)
                except:
                    m = str(datetime.datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S")) + ' ' + pair + ' ' + timeframe + ' failed to fill. Records: ' + str(
                        len(candel_list))
                    logging.info(m)
                    print(m)
                    pass
        # Avoid blocked API
        time.sleep(3)


def run_dbfill():
    ################### CONFIG ###################

    conf = internal.Config('config.ini', 'services')
    db_name = conf['db_name']
    host = conf['host']
    port = int(conf['port'])
    limit = int(conf['fill_limit'])

    pairs = conf['pairs'].split(',')
    timeframes = conf['fill_timeframes'].split(',')

    ##############################################

    client = InfluxDBClient(host, port, 'root', 'root', db_name)

    for pair in pairs:
        bitfinex_fill(client, pair, timeframes, limit)


