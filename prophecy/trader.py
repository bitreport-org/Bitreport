import portfolios
import strategies


class Trader:    
    def __init__(self, name, portfolio, strategy=None):
        """
        name - just a fancy thing
        protfolio - instance of a portfolio
        """
            
        self.name = name
        
        assert isinstance(portfolio, portfolios.Portfolio), \
        'Portfolio must be instance of Portfolio, not {}'.format(type(portfolio))
        self.portfolio = portfolio
        
        if strategy:
            assert isinstance(strategy, strategies.BaseStrategy), 'Strategy must be instance of BaseStrategy'
            assert hasattr(strategy, "decide"), 'Strategy must have decide method'
            
        self.startegy = strategy
        
    def __repr__(self):

        m =  "TRADER {} \n \
        Portfolio: {} \n \
        -- Cash: {} \n \
        -- Coins: {} \n \
        -- Trades {} \n \
        Last trade: \n \
        {} {} {} at {} \n \
        Default startegy: {} \
        ".format(self.name, 
                 type(self.portfolio).__name__,
                 self.portfolio.cash,
                 self.portfolio.coins,
                 self.portfolio.trades,
                 self.portfolio.last_trade['action'].upper(),
                 self.portfolio.last_trade['amount'],
                 self.portfolio.pair.upper(),
                 self.portfolio.last_trade['price'],
                 type(self.startegy).__name__)
        return m
    
        
    def trade(self, data, strategy=None):
        """
        strategy - a method with returns  a tuple (action, actual_price)
                    where action is one of short/long/keep
        """
        if not strategy:
            print('Using default strategy')
            strategy = self.strategy
            
        if not strategy:
            print('No default strategy.')
            return False
        
        assert isinstance(strategy, strategies.BaseStrategy)
        assert hasattr(strategy, "decide")
        
        action, actual_price = strategy.decide(data, self)
        assert action in ['keep', 'short', 'long'], 'Only keep/short/long actions are allowed'
        
        # Makes a trade
        self.portfolio.update(action, actual_price)
        
        if action != 'keep':
            return True
    
        return False
        