from influxdb import InfluxDBClient


################################ REST ####################################################
from datetime import datetime, timedelta
import requests

#
# # using Http
# # client = InfluxDBClient(database='dbname')
# # client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example2')
# # client = InfluxDBClient(host='127.0.0.1', port=8086, username='root', password='root', database='dbname')
#
#
# def write_ticker2(ticker, client, pair_list):
#     json_body = []
#     utcnow = datetime.utcnow()
#
#     for i in range(0, len(pair_list)):
#         json_body = [
#             {
#                 "measurement": ticker[i][0],
#                 "time": utcnow,
#                 "fields": {
#                     "BID": float(ticker[i][1]),
#                     "BID_SIZE": float(ticker[i][2]),
#                     "ASK": float(ticker[i][3]),
#                     "ASK_SIZE": float(ticker[i][4]),
#                     "DAILY_CHANGE": float(ticker[i][5]),
#                     "DAILY_CHANGE_PERC": float(ticker[i][6]),
#                     "LAST_PRICE": float(ticker[i][7]),
#                     "VOLUME": float(ticker[i][8]),
#                     "HIGH": float(ticker[i][9]),
#                     "LOW": float(ticker[i][10]),
#                 }
#             }
#         ]
#         client.write_points(json_body)
#
#
# def service(client, db_name, pair_list, timeframes):
#
#     for timeframe in timeframes:
#         for pair in pair_list:
#             # Continuous Queries for each par for each period
#             # create cq BTCUSD1h on DATABASE begin ... into BTCUSD1h from tBTCUSD group by time(1h) end
#
#             query = 'CREATE CONTINUOUS QUERY '+ pair + timeframe + ' ON ' + db_name +' BEGIN SELECT \
#                     first(LAST_PRICE) AS open, \
#                     max(LAST_PRICE) AS high, \
#                     min(LAST_PRICE) AS low, \
#                     last(LAST_PRICE) AS close, \
#                     last(LAST_PRICE) AS volume  \
#                     INTO ' + pair + timeframe + ' FROM t' + pair +' GROUP BY time(' +timeframe+ ') END'
#
#             client.query(query)
#
#             # Retention policy
#             # https://influxdb-python.readthedocs.io/en/latest/api-documentation.html#influxdbclient
#             # create_retention_policy(name, duration, replication, database=None, default=False)
#
#     # build string for url
#     str = ''
#     for pair in pair_list:
#         str = str + 't' + pair+ ','
#
#     # get ticker every 60 seconds
#     while True:
#         start = time.time()
#
#         # GET Bitfinex API
#         url = 'https://api.bitfinex.com/v2/tickers?symbols=' + str
#         ticker = requests.get(url).json()
#         write_ticker2(ticker, client, pair_list)
#         #print(client.query('select * from tBTCUSD ORDER BY time DESC LIMIT 1;'))
#
#         # Next run in 60sec - execution time
#         t = 60 - (time.time() - start)
#         time.sleep(t)
#
#
# # PARAMETERS
# db, pairs, timeframes = 'test2', ['BTCUSD'], ['15m','1h']
# list = [
# 'ETH' ,
# 'EOS' ,
# 'LTC' ,
# 'ETC' ,
# 'OMG' ,
# 'BCH' ,
# 'NEO' ,
# 'XMR' ,
# 'XRP' ,
# 'ETP' ,
# 'ZEC' ,
# 'DAS' ,
# 'EDO' ,
# 'SAN' ,
# 'IOTA'
# ]
#
#
#
# # # CONNECT DATABASE
# # client = InfluxDBClient('localhost', 8086, 'root', 'root', db)
# # client.create_database(db)
# #
# # service(client, db, pairs, timeframes)

import websocket
import _thread
import time
import ast

################################## WEBSOCKETS ############################################

class bitfinex_pair_dbservice():

    def __init__(self, db_name, pair ):
        self.client = InfluxDBClient('localhost', 8086, 'root', 'root', db_name)
        self.start = time.time()
        self.db = db_name
        self.last1 = 0
        self.last2 =0
        self.pair = pair
        self.client.create_database(db_name)
        self.connected = 0

    # Creates Continuous Query with a given timeframe
    def create_conquery(self, timeframe ):
        # Continuous Queries for each par for each period
        # create cq BTCUSD1h on DATABASE begin ... into BTCUSD1h from tBTCUSD group by time(1h) end

        query = 'CREATE CONTINUOUS QUERY ' + self.pair + timeframe + ' ON ' + self.db + ' BEGIN SELECT \
                           first(LAST_PRICE) AS open, \
                           max(LAST_PRICE) AS high, \
                           min(LAST_PRICE) AS low, \
                           last(LAST_PRICE) AS close, \
                           last(LAST_PRICE) AS volume  \
                           INTO ' + self.pair + timeframe + ' FROM t' + self.pair + ' GROUP BY time(' + timeframe + ') END'

        self.client.query(query)

    # Writes candlestick from message to InfluxDB
    def write_ticker(self, ticker):
        json_body = [
            {
                "measurement": self.pair,
                "time": ticker[0],
                "fields": {
                    "open": float(ticker[1]),
                    "close": float(ticker[2]),
                    "high": float(ticker[3]),
                    "low": float(ticker[4]),
                    "volume": float(ticker[5]),
                }
            }
        ]
        self.client.write_points(json_body)

    # Websocket messages handler
    def on_message(self, ws, message):
        # Handling first message beacuse ast.literal_eval doesn't work
        if self.connected < 2:
            print('Connected!')
            self.connected +=1
        else:
            response = ast.literal_eval(message)[1]
            if response != 'hb':
                now = time.time()
                if now - self.start >= 60 and response[0]!= self.last1 and response[0] != self.last2:
                    print(ast.literal_eval(message)[1], time.time())
                    self.start = now
                    self.last2 = self.last1
                    self.last1 = response[0]
                    self.write_ticker(response)


    def on_error(self, ws, error):
        print('error')

    def on_close(self, ws):
        print("### closed ###")

    # Subscribe to new channel
    def on_open(self, ws):
        def run(*args):
            ws.send('{ \
                        "event": "subscribe",\
                        "channel": "candles", \
                        "key": "trade:1m:t' + self.pair +'" \
                    }')
        _thread.start_new_thread(run, ())




def bitfinex_create_service(db_name, pair, timeframes, retentions='none'):
    # Connect websockets
    service = bitfinex_pair_dbservice(db_name, pair)

    # Continuous queries
    for tf in timeframes:
        service.create_conquery(tf)

    # Websocket channel
    ws = websocket.WebSocketApp("wss://api.bitfinex.com/ws/2",
                                on_message=service.on_message,
                                on_error=service.on_error,
                                on_close=service.on_close)
    ws.on_open = service.on_open
    ws.run_forever()


if __name__ == "__main__":


    # PARAMS
    db_name = 'test3'

    pairs = ['BTCUSD']

    timeframes = ['30m', '1h', '2h', '3h', '6h', '12h', '24h', '168h']

    # Creates bitfinex api services
    websocket.enableTrace(True)
    for pair in pairs:
        bitfinex_create_service(db_name, pair, timeframes)
