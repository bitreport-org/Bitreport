from influxdb import InfluxDBClient
from datetime import datetime
import datetime
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
        self.i = 0

    # Creates Continuous Query with a given timeframe
    def create_conquery(self, timeframe):
        # Continuous Queries for each par for each period
        # create cq BTCUSD1h on DATABASE begin ... into BTCUSD1h from tBTCUSD group by time(1h) end

        query = 'CREATE CONTINUOUS QUERY ' + self.pair + timeframe + ' ON ' + self.db + ' RESAMPLE EVERY 5m BEGIN SELECT  \
                           first(open) AS open, \
                           max(high) AS high, \
                           min(low) AS low, \
                           last(close) AS close, \
                           sum(volume) AS volume  \
                           INTO ' + self.pair + timeframe + ' FROM ' + self.pair + ' GROUP BY time(' + timeframe + ') END'

        self.client.query(query)

    #
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
        self.client.write_points(json_body)


    #Websocket messages handler
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
                    print(self.i, datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), ast.literal_eval(message)[1])
                    self.write_ticker(response)
                    self.start = now
                    self.last2 = self.last1
                    self.last1 = response[0]
                    self.i += 1

    def on_error(self, ws, error):
        print('Error. Time : ', datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

    def on_close(self, ws):
        print("Connection closed. Time : ", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))

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

    # Retention policy


    # Websocket channel
    ws = websocket.WebSocketApp("wss://api.bitfinex.com/ws/2",
                                on_message=service.on_message,
                                on_error=service.on_error,
                                on_close=service.on_close)
    ws.on_open = service.on_open
    ws.run_forever()


#################################### MAIN ################################################
if __name__ == "__main__":

    # PARAMS
    db_name = 'test'

    pairs = ['BTCUSD']

    timeframes = ['5m', '30m', '1h', '2h', '3h', '6h', '12h', '24h', '168h']

    # Creates bitfinex api services
    websocket.enableTrace(True)
    for pair in pairs:
        bitfinex_create_service(db_name, pair, timeframes)
