from strategies.strategy import Strategy


class Arbitrage(Strategy):

    def __init__(self, exchange, timeout=60, *args, **kwargs):
        super().__init__(exchange, timeout)

        self.exchanges = ['binance', 'bitfinex', 'kraken']
        self.currencies = ['bitcoin', 'ethereum', 'monero']
        self.asset = ['EUR']

    def run(self):
            coin_data = []
            for coin in self.currencies:
                response = self.exchange.get_client().get_symbol_ticker()
                print(response)