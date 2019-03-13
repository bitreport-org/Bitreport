class Portfolio:
    """
    pair - name of traded pair
    coins - amout of coins in possesion
    cash - amount of cash in posession
    trades - number of trades 
    last_trade - dictionary with information about last trade
    """
    
    def __init__(self, pair, start_amount):
        """
        pair - name of traded pair
        start_amount - initail amount of cach
        """
        self.pair = pair
        self.cash = start_amount
        self.coins = 0.0
        self.trades = 0
        self.last_trade = {'price': 0, 'amount': 0, 'action': 'None'}
                
    def stats(self):
        return {'cash': self.cash, 'coins': self.coins, 
                'trades': self.trades, 'last_trade': self.last_trade}
    
    def update(self, action, actual_price):
        print('No portfolio type.')
    
    
class SimpleBuySell(Portfolio):
    def update(self, action, actual_price):
        if action == 'short' and self.coins > 0.0 :
            self.last_trade = {'price': actual_price, 'amount': self.coins, 'action': 'short'}
            self.cash += self.coins * actual_price
            self.coins = 0.0
            self.trades += 1
        
        elif action == 'long' and self.cash > 0:
            self.last_trade = {'price': actual_price, 'amount': self.cash, 'action': 'short'}
            self.coins += self.cash / actual_price
            self.cash = 0.0
            self.trades += 1
            
class SimpleShortLong(Portfolio):
    def update(self, action, actual_price):
        NotImplemented
        