from exchanges import exchange


class Coinbase(exchange.Exchange):
    def __init__(self, key: str, secret: str):
        exchange.Exchange.__init__(self, key, secret)
        # self.client = CoinbaseAccount(self.api_key, self.api_secret)
        self.name = self.__class__.__name__

    def get_client(self):
        return self.client

    def symbol_ticker(self):
        response = self.client.exchange_rates(['usd_to_btc'])
        self.process(response)
