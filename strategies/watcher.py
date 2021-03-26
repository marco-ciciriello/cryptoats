from models import price
from strategies.strategy import Strategy


class Watcher(Strategy):

    def __init__(self, exchange, timeout=60, *args, **kwargs):
        super().__init__(exchange, timeout)

    def run(new_price: price.Price):
        print('*******************************')
        print('Exchange: ', new_price.exchange)
        print('Pair: ', new_price.pair)
        print('Price: ', new_price.current)
