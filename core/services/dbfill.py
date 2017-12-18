import requests
from influxdb import InfluxDBClient
from services import internal
import time

def bitfinex_fill(client, db, pair, timeframes, limit):
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
                    print(pair, timeframe, 'filled successfully! Records:', len(candel_list))
                except:
                    print(pair, timeframe, 'failed to fill.Records:', len(candel_list))
                    pass
        # Avoid blocked API
        time.sleep(4)

if __name__ == "__main__":
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
        bitfinex_fill(client, db_name, pair, timeframes, limit)
