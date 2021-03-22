from twisted.internet import reactor

from binance.client import Client
from binance.websockets import BinanceSocketManager

from exchanges import exchange
from models import price


class Binance(exchange.Exchange):

    def __init__(self, key: str, secret: str) -> None:
        exchange.Exchange.__init__(self, key, secret)
        self.client = Client(self.api_key, self.api_secret)

    def get_client(self) -> Client:
        return self.client

    def get_socket_manager(self) -> BinanceSocketManager:
        return BinanceSocketManager(self.client)

    def get_candles(self, interval=Client.KLINE_INTERVAL_1MINUTE):
        response: object = self.client.get_klines(symbol=self.symbol, interval=interval)
        print(response)

    def get_historical_candles(self, start: str, end=None, interval=Client.KLINE_INTERVAL_1MINUTE):
        for candle in self.client.get_historical_klines_generator(self.symbol, interval, start, end):
            print(candle)

    def symbol_ticker(self):
        response = self.client.get_symbol_ticker(self.symbol)
        print(response)
        self.process(response)

    def start_symbol_ticker_socket(self, symbol: str) -> None:
        self.socketManager = self.get_socket_manager()
        self.socket = self.socketManager.start_symbol_ticker_socket(symbol, self.process_message)
        self.start_socket()

    def start_socket(self) -> None:
        print('*' * 20, 'Starting WebSocket connection', '*' * 20)
        self.socketManager.start()

    def close_socket(self) -> None:
        self.socketManager.stop_socket(self.socket)
        self.socketManager.close()
        reactor.stop()

    def process_message(self, msg) -> None:
        if msg['e'] == 'error':
            print(msg)
            self.close_socket()
        else:
            new_price = price.Price(pair=self.symbol, curr=float(msg['b']), lowest=float(msg['l']),
                                    highest=float(msg['h']))
            self.strategy.run(new_price)
