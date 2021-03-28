from models.price import Price
from strategies.strategy import Strategy


class Watcher(Strategy):

    def __init__(self, exchange, timeout=60, *args, **kwargs):
        super().__init__(exchange, timeout)

    def run(self):
        response = self.exchange.symbol_ticker()
        new_price = Price(pair=self.exchange.get_symbol(), currency=self.exchange.currency, asset=self.exchange.asset,
                          exchange=self.exchange.name, current=response['price'])

        print('*******************************')
        print('Exchange: ', new_price.exchange)
        print('Pair: ', new_price.pair)
        print('Price: ', new_price.current)
