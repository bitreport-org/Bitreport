import requests
from influxdb import InfluxDBClient



def bitfinex_fill(client, db, pair, timeframes, limit):
    for timeframe in timeframes:
        url = 'https://api.bitfinex.com/v2/candles/trade:' + timeframe + ':t' + pair + '/hist?limit=' + str(
            limit) + '&start=946684800000'
        candel_list = requests.get(url).json()
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


if __name__ == "__main__":
    # PARAMETERS
    db = 'test'
    client = InfluxDBClient('localhost', 8086, 'root', 'root', db)

    pair = 'BTCUSD'
    timeframes = ['30m', '1h', '3h', '12h']

    bitfinex_fill(client, db, pair, timeframes, 100)
