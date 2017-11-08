from flask import Flask
from flask_restful import Resource, Api
from influxdb import InfluxDBClient

app = Flask(__name__)
api = Api(app)
db = 'test'

class GET_OHLC(Resource):
    def get(self, db, pair, timeframe, limit):
        # Connect to databse
        client = InfluxDBClient('localhost', 8086, 'root', 'root', db)

        # Perform query and return JSON data
        query = 'SELECT * FROM ' + pair + timeframe + ' ORDER BY time DESC LIMIT ' + str(limit) + ';'
        params = 'db=' + db + '&q=' + query
        r = client.request('query', params=params)

        # Unwrap json :D
        return r.json()['results'][0]['series'][0]['values']


api.add_resource(GET_OHLC, '/<string:db>/<string:pair>/<string:timeframe>/<int:limit>')

if __name__ == '__main__':
    app.run()