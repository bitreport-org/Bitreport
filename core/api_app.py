from flask import Flask
from flask_restful import Resource, Api
from influxdb import InfluxDBClient

app = Flask(__name__)
api = Api(app)


db = 'test3'
client = InfluxDBClient('localhost', 8086, 'root', 'root', db)

class get_ohlc(Resource):
    def get(self, pair, timeframe, limit):
        global client, db

        # Perform query and return JSON data
        query = 'SELECT * FROM ' + pair + timeframe + ' ORDER BY time DESC LIMIT ' + str(limit) + ';'
        params = 'db=' + db + '&q=' + query
        r =client.request('query', params=params)

        # Unwrap json :D
        return r.json()['results']#[0]['series'][0]['values']


class get_pair(Resource):
    def get(self, pair):
        global client, db

        # Perform query and return JSON data
        query = 'SELECT * FROM ' + pair + ';'
        params = 'db=' + db + '&q=' + query
        r = client.request('query', params=params)

        # Unwrap json :D
        return r.json()['results'][0]['series'][0]['values']


api.add_resource(get_ohlc, '/candles/<string:pair>/<string:timeframe>/<int:limit>')
api.add_resource(get_pair, '/<string:pair>')

if __name__ == '__main__':
    app.run()