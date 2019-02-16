import numpy as np
import pandas as pd
import time
import logging
import requests

from influxdb import InfluxDBClient
from keras.models import load_model
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error


# Henry the market-beating bot for Bitmex
class Henry:
    def __init__(self, influx, start_amount=1000):
        self.name = 'Henry'
        self.influx = influx
        self.start_amount = float(start_amount)
        self.budget = 0.0
        self.market = 0.0
        self.coins = 0.0
        self.fee = 0.008
        self.last_buy = 1000000000000000.0
        self.last_sell = 0.0

        # self.model = load_model('models/size20future1_110219.h5')
        self.model = load_model('models/size50future3_130219.h5')
        self.model_size = int(self.model.input.shape[1])
        self.future = 3

    def _fetch_data(self, symbol='XBT'):
        url = f'https://www.bitmex.com/api/v1/trade/bucketed?binSize=1m&partial=false&symbol={symbol}&count=20&reverse=false'
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f'Bitmex request failed')
            return False

        last_price = pd.DataFrame(response.json())
        last_price = last_price[['close','high', 'low', 'open', 'volume']].iloc[:self.model_size, :]

        return last_price

    def _save_decision(self, info):
        data = [{
                "measurement": self.name.lower(),
                "time": int(1000*time.time()),
                "fields": info
            }]

        result = self.influx.write_points(data, time_precision='ms')
        if not result:
            print(f'Sir {self.name} has problems with saving his decision.')
            logging.info(f'Sir {self.name} has problems with saving his decision.')

    def _dir(self, a, b, p):
        if b > a and p > a:
            return 1.0
        elif b < a and p < a:
            return 1.0
        else:
            return 0.0

    def _read_last_decision(self):
        # TODO: Read last record from measurement
        measurement = self.name.lower()
        r = self.influx.query(f'SELECT * FROM {measurement} ORDER BY time ASC;', epoch='ms')
        df = pd.DataFrame(list(r.get_points(measurement=measurement)))

        if df.shape == (0, 0):
            stats = {'rmse': None, 'mae': None, 'dir': None}
            return self.coins, self.start_amount, stats

        if df.shape[0] < self.future+1:
            stats = {'rmse': None, 'mae': None, 'dir': None}
            return float(df.coins.values[-1]), float(df.budget.values[-1]), stats

        # Calculate some stats

        y = df.price.values[self.future:]
        y_lag = df.price.values[:-self.future]
        y_hat = df.prediction.values[:-self.future]

        # direction success
        da = np.mean([self._dir(a, b, p) for a, b, p in zip(y_lag, y, y_hat)]) #Directional Accuracy
        stats = {
            'mse': float(mean_squared_error(y, y_hat)),
            'mae': float(mean_absolute_error(y, y_hat)),
            'r2': float(r2_score(y, y_hat)),
            'da': da
        }

        return float(df.coins.values[-1]), float(df.budget.values[-1]), stats


    def _process(self, window: pd.DataFrame):
        M = np.max(window.high.values)
        m = np.min(window.low.values)
        d = M - m
        output = (window.iloc[:, :-1] - m) / d
        vol = window.volume.values
        vol = (vol - np.min(vol)) / (np.max(vol) - np.min(vol))
        assert output.shape[0] == vol.size, "Candles and volume sizes differ"

        output = np.array([np.concatenate([o, [x]]) for o, x in zip(output.values, vol)])

        return output, M, m

    def _rescale(self, predicted_price, M, m):
        return (M - m) * predicted_price + m

    def _predict(self, df):
        recent_price = df.close.values[-1]
        output, M, m = self._process(df)
        # output = self._reshape(output)

        predicted_price = self.model.predict([[output]])[0][0]
        predicted_price = self._rescale(predicted_price, M, m)

        return recent_price, predicted_price

    def _market_value(self, price):
        if self.coins > 0:
            return price * self.coins
        else:
            return self.budget

    def _buy(self, price):
        self.coins = self.budget / price * (1 - self.fee)
        self.budget = 0.0
        self.last_buy = price

    def _sell(self, price):
        self.budget = self.coins * price * (1 - self.fee)
        self.coins = 0.0
        self.last_buy = 1000000000000000.0


    def _strategy(self, price, prediction):
        decision = 'keep'

        if prediction >= price and self.coins == 0.0:
            trade_cost = self.budget * self.fee
            potential_profit = self.budget * (prediction - price)

            if potential_profit > trade_cost:
                self._buy(price)
                decision = 'buy'

        if prediction < self.last_buy * 0.98 and self.coins != 0.0:
            self._sell(price)
            decision = 'sell'

        if decision == 'keep':
            self.last_buy = self.last_buy * 1.002

        return decision


    def decide(self, df):
        # Data process
        # df = self._fetch_data(pair)
        assert df.shape[0] == self.model_size, 'Wrong input size'
        recent_price, predicted_price = self._predict(df)

        # Decision proceess
        self.coins, self.budget, stats = self._read_last_decision()
        decision = self._strategy(recent_price, predicted_price)

        info = {
            'decision': decision,
            'price': recent_price,
            'prediction': predicted_price,
            'budget': self.budget,
            'coins': self.coins,
            'market': self._market_value(recent_price),
        }
        info.update(stats)

        # logging.info(f"Sir {self.name} decided to {info['decision'].upper()}, his present net wealth: {info['market']}")
        print(f"Sir {self.name} decided to {info['decision'].upper()}, his present net wealth: {info['market']}")
        # print(stats)

        self._save_decision(info)
        return info


if __name__ == '__main__':
    influx = InfluxDBClient('0.0.0.0', 5002, 'root', 'root', 'test')
    influx2 = InfluxDBClient('0.0.0.0', 5002, 'root', 'root', 'pairs')
    influx.drop_database('test')
    influx.create_database('test')

    henry = Henry(influx, start_amount=100 )

    measurement = 'BTCUSD6h'
    r = influx2.query(f'SELECT * FROM {measurement} ORDER BY time ASC;', epoch='ms')
    df = pd.DataFrame(list(r.get_points(measurement=measurement)))

    epochs = 50
    for i in range(epochs):
        window = df.iloc[i:i + 52, :]
        window = window.sort_values(by="time")
        window = window[['close', 'high', 'low', 'open', 'volume']]
        henry.decide(window)
        time.sleep(0.03)

    r = influx.query('SELECT * FROM henry ORDER BY time DESC;', epoch='ms')
    df = pd.DataFrame(list(r.get_points(measurement='henry')))
    print(df)