from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

class portfolio:
    def __init__(self, start_amount: float, model, fee=0.04):
        assert start_amount > 0, 'Want to play with no money?'
        self.start_amount = start_amount
        self.budget = start_amount  # dolars
        self.coins = 0
        self.fee = fee
        self.model = model
        self.history = []

    def _process(self, window: pd.DataFrame):
        M = np.max(np.max(window))
        m = np.min(np.min(window))
        d = M - m
        output = (window - m) / d
        return output, M, m

    def _reshape(self, window: pd.DataFrame, size):
        return window.values.reshape(size, 4)

    def _rescale(self, predicted_price, M, m):
        return (M - m) * predicted_price + m

    def _buy(self, price):
        self.coins = self.budget / price * (1 - self.fee)
        self.budget = 0

    def _sell(self, price):
        self.budget = self.coins * price * (1 - self.fee)
        self.coins = 0

    def _decide(self, price, prediction, epoch):
        if prediction >= price and self.coins == 0:
            trade_cost = self.budget * self.fee
            potential_profit = self.budget * (prediction - price)
            if potential_profit > trade_cost:
                self._buy(price)
                print(f'Epoch: {epoch} : BUY - actual: {price} predicted: {prediction}')
                self.history.append(('buy', price, prediction, self.coins, self.budget))

        if prediction < price and self.coins != 0:
            trade_cost = self.coins * price * self.fee
            potentail_loss = self.coins * (price - prediction)
            if potentail_loss > trade_cost:
                self._sell(price)
                print(f'Epoch: {epoch} : SELL - actual: {price} predicted: {prediction}')
                self.history.append(('sell', price, prediction, self.coins, self.budget))

    def simulate(self, df: pd.DataFrame, size):
        # TODO: assert smth ! !
        y, y_hat = [], []
        self.epochs = df.shape[0] - size
        for i in range(self.epochs):
            window = df.iloc[i:i + size, :]
            recent_price = window.close.values[-1]

            if i == 0:
                self._buy(recent_price)

            output, M, m = self._process(window)
            output = self._reshape(output, size)

            predicted_price = self.model.predict([[output]])[0][0]
            predicted_price = self._rescale(predicted_price, M, m)
            y.append(recent_price)
            y_hat.append(predicted_price)
            self._decide(recent_price, predicted_price, epoch=i)

        # make last trade
        if self.coins != 0:
            self._sell(recent_price)

        #  For plots
        self.y = y[1:]
        self.y_hat = y_hat

        self.summary()

    def summary(self):
        print('Portfolio summary')
        print(f'Transaction fee: {self.fee}')
        print(f'Start amount: {self.start_amount}')
        print(f'Final amount: {self.budget}')
        print(f'Earnings : {(self.budget - self.start_amount):.2f}')
        print(f'Profit : {100*(self.budget/self.start_amount -1):.2f}%')
        print(f'Decision points: {self.epochs}')
        print( f"Decisions made : {len(self.history)}, \
                buy: {len([x for x in self.history if x[0]=='buy'])} \
                sell: {len([x for x in self.history if x[0]=='sell'])}")

    def plot_history(self):
        coins = [x[3] for x in self.history if x[3] != 0]
        plt.plot(coins)
        plt.title('Coins history')
        plt.show()

        budget = [x[4] for x in self.history if x[4] != 0]
        plt.plot(budget)
        plt.title('Budget history')
        plt.show()

    def plot_prediction(self):
        plt.plot(self.y)
        plt.plot(self.y_hat, color='orange')
        plt.show()