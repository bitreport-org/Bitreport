import yaml
import portfolios
import strategies
from trader import Trader

class Desk:
    def __init__(self):
        self.traders = dict()
    
    def read_desk(self, filename, verbose=True):
        assert isinstance(filename, str)
        with open(filename) as f:
            yaml_data = yaml.load(f)
        
        for t in yaml_data:
            self.add_trader(t['trader'])
            
        if verbose:
            self.summary()
            
        return self
        
    def summary(self):
        for t in self.traders.values():
            print(t)
        
    def add_trader(self, trader):
        p = getattr(portfolios, trader['portfolio'], None)
        s = getattr(strategies, trader.get('strategy', 'None'), None)
        if s:
            s = s ()
            
        self.traders[trader['name']] = Trader(
            name=trader['name'],
            portfolio=p(
                pair=trader['pair'], 
                start_amount=trader['start_amount']),
            strategy=s
        )
        
    def remove_trader(self, name):
        if not self.traders.pop(name, None):
            print('Trader does not exists.')
            
    def get_trader(self, name):
        return self.traders.get(name, None)
    
    def show_trader(self, name):
        print(self.traders.get(name, 'Trader does not exist'))
        
    def make_trade(self, trader_name, data, strategy=None):
        t = self.get_trader(trader_name)
        if not t:
            print('Trader does not exist')
        # Make a trade
        return t.trade(data, strategy)
            
        