from influxdb import InfluxDBClient
from datetime import datetime
import websocket
import ast
from threading import Thread
import threading
import time
import os
from services import internal
import datetime

################################## WEBSOCKETS ############################################

class bitfinex_pair_dbservice():
    def __init__(self, db_name, host, port, pair, timeframes ):
        self.client = InfluxDBClient(host, port, 'root', 'root', db_name)
        self.db = db_name
        self.last1 = 0
        self.last2 =0
        self.pair = pair
        self.client.create_database(db_name)
        self.timeframes = timeframes

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

    # Writes error message
    def write_error(self, message, pair):
        json_body = [
            {
                "measurement": 'Error',
                "time": int(time.mktime(datetime.datetime.now().timetuple())) * 1000000000,
                "tags": {
                    "Message": message,
                    "Pair" : pair,
                }
            }
        ]
        status = self.client.write_points(json_body)

    #Websocket messages handler
    def on_message(self, ws, message):
        try:
            response = ast.literal_eval(message)[1]
            if response != 'hb':
                # Dump handling - normal ticker message has 6 values, dump is a longer message
                if len(response) > 6:
                    for ticker in response:
                        self.write_ticker(ticker)
                        #print(self.pair, ' dump record : ', datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), ticker)
                    print(self.pair, 'dump saved.', len(response), 'records.')

                # Single ticker handling
                elif  response[0]!= self.last1 and response[0] != self.last2:
                    try:
                        status = self.write_ticker(response)
                        #print(self.pair, ' ticker :',datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), response, status)
                        self.last2 = self.last1
                        self.last1 = response[0]
                    except:
                        print('Ticker write failed', self.pair)
                        pass
        except:
            print(self.pair, 'connected!')
            pass

    def on_error(self, ws, error):
        message = self.pair + 'Error. Time : ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.write_error(message, self.pair)
        print(message)
        self.on_open(ws)

    def on_close(self, ws):
        message = self.pair + 'Connection closed. Time : ' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.write_error(message, self.pair)
        print(message)
        self.on_open(ws)

    # Subscribe to new channel
    def on_open(self, ws):
        def run(*args):
            ws.send('{ \
                        "event": "subscribe",\
                        "channel": "candles", \
                        "key": "trade:1m:t' + self.pair +'" \
                    }')

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

#################################### MAIN ################################################
if __name__ == "__main__":

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
        service= bitfinex_pair_dbservice(db_name, host, port, pair, timeframes)
        threads.append(threading.Thread(target=service.create))

    for t in threads:
        t.setDaemon(True)

    for t in threads:
        t.start()

    clear = lambda: os.system('clear')
    while True:
        print('Active threads:', threading.active_count()-1)
        time.sleep(60*5)
        #clear()



