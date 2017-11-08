from influxdb import InfluxDBClient
from datetime import datetime, timedelta
import requests
import time

# using Http
# client = InfluxDBClient(database='dbname')
# client = InfluxDBClient('localhost', 8086, 'root', 'root', 'example2')
# client = InfluxDBClient(host='127.0.0.1', port=8086, username='root', password='root', database='dbname')


def write_ticker(ticker, client, pair_list):
    json_body = []
    utcnow = datetime.utcnow()

    for i in range(0, len(pair_list)):
        json_body = [
            {
                "measurement": ticker[i][0],
                "time": utcnow,
                "fields": {
                    "BID": float(ticker[i][1]),
                    "BID_SIZE": float(ticker[i][2]),
                    "ASK": float(ticker[i][3]),
                    "ASK_SIZE": float(ticker[i][4]),
                    "DAILY_CHANGE": float(ticker[i][5]),
                    "DAILY_CHANGE_PERC": float(ticker[i][6]),
                    "LAST_PRICE": float(ticker[i][7]),
                    "VOLUME": float(ticker[i][8]),
                    "HIGH": float(ticker[i][9]),
                    "LOW": float(ticker[i][10]),
                }
            }
        ]
        client.write_points(json_body)









def service(client, db_name, pair_list, timeframes):

    for timeframe in timeframes:
        for pair in pair_list:
            # Continuous Queries for each par for each period
            # create cq BTCUSD1h on DATABASE begin ... into BTCUSD1h from tBTCUSD group by time(1h) end

            query = 'CREATE CONTINUOUS QUERY '+ pair + timeframe + ' ON ' + db_name +' BEGIN SELECT \
                    first(LAST_PRICE) AS open, \
                    max(LAST_PRICE) AS high, \
                    min(LAST_PRICE) AS low, \
                    last(LAST_PRICE) AS close, \
                    last(LAST_PRICE) AS volume  \
                    INTO ' + pair + timeframe + ' FROM t' + pair +' GROUP BY time(' +timeframe+ ') END'

            client.query(query)

            # Retention policy
            # https://influxdb-python.readthedocs.io/en/latest/api-documentation.html#influxdbclient
            # create_retention_policy(name, duration, replication, database=None, default=False)

    # build string for url
    str = ''
    for pair in pair_list:
        str = str + 't' + pair+ ','

    # get ticker every 60 seconds
    while True:
        start = time.time()

        # GET Bitfinex API
        url = 'https://api.bitfinex.com/v2/tickers?symbols=' + str
        ticker = requests.get(url).json()
        write_ticker(ticker, client, pair_list)
        #print(client.query('select * from tBTCUSD ORDER BY time DESC LIMIT 1;'))

        # Next run in 60sec - execution time
        t = 60 - (time.time() - start)
        time.sleep(t)


# PARAMETERS
db, pairs, timeframes = 'test2', ['BTCUSD'], ['15m','1h']
list = [
'ETH' ,
'EOS' ,
'LTC' ,
'ETC' ,
'OMG' ,
'BCH' ,
'NEO' ,
'XMR' ,
'XRP' ,
'ETP' ,
'ZEC' ,
'DAS' ,
'EDO' ,
'SAN' ,
'IOTA'
]



# CONNECT DATABASE
client = InfluxDBClient('localhost', 8086, 'root', 'root', db)
client.create_database(db)

service(client, db, pairs, timeframes)



