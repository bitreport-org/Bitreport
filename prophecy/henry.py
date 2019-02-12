import numpy as np
import pandas as pd
import time


# Henry the market-beating bot for Bitmex
class Henry:
    def __init__(self, influx, model, size):
        self.measurement = 'henry'
        self.influx = influx
        self.start_amount = 0
        self.budget = 0
        self.market = 0
        self.coins = 0
        self.fee = 0.008

        # TODO: use path to model
        self.model = model
        self.model_size = size

    def _fetch_data(self):
        # TODO: assert shapes, errors etc
        return pd.DataFrame([])

    def _save_decision(self, info):
        data = [{
                "measurement": self.measurement,
                "time": int(time.time()),
                "fields": info
            }]

        result = self.influx.write_points(data, time_precision='s')
        #TODO: check if write successful

    def _read_last_decision(self):
        # TODO: Read last record from measurement
        NotImplemented

    def _process(self, window: pd.DataFrame):
        M = np.max(np.max(window))
        m = np.min(np.min(window))
        d = M - m
        output = (window - m) / d
        return output, M, m

    def _reshape(self, window: pd.DataFrame):
        return window.values.reshape(self.model_size, 4)

    def _rescale(self, predicted_price, M, m):
        return (M - m) * predicted_price + m

    def _predict(self, df):
        recent_price = df.close.values[-1]
        output, M, m = self._process(df)
        output = self._reshape(output)

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
        self.budget = 0

    def _sell(self, price):
        self.budget = self.coins * price * (1 - self.fee)
        self.coins = 0

    def _strategy(self, price, prediction):
        decision = 'keep'

        if prediction >= price and self.coins == 0:
            trade_cost = self.budget * self.fee
            potential_profit = self.budget * (prediction - price)
            if potential_profit > trade_cost:
                self._buy(price)
                # print(f'BUY - actual: {price} predicted: {prediction}')
                decision = 'buy'

        if prediction < price and self.coins != 0:
            trade_cost = self.coins * price * self.fee
            potentail_loss = self.coins * (price - prediction)
            if potentail_loss > trade_cost:
                self._sell(price)
                # print(f'SELL - actual: {price} predicted: {prediction}')
                decision = 'sell'

        return decision


    def decide(self):
        # Data process
        df = self._fetch_data()
        recent_price, predicted_price = self._predict(df)

        # Decision proceess
        self._read_last_decision()
        decision = self._strategy(recent_price, predicted_price)

        info = {
            'decision': decision,
            'price': recent_price,
            'prediction': predicted_price,
            'budget': self.budget,
            'coins': self.coins,
            'market': self._market_value(recent_price)
        }

        self._save_decision(info)
        return info
