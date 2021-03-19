from twisted.internet import reactor

from binance.client import Client
from binance.websockets import BinanceSocketManager

from exchanges import exchange


class Binance(exchange.Exchange):

    def __init__(self, key: str, secret: str) -> None:
        exchange.Exchange.__init__(self, key, secret)
        self.client = Client(self.api_key, self.api_secret)

    def get_client(self) -> Client:
        return self.client

    def get_socket_manager(self) -> BinanceSocketManager:
        return BinanceSocketManager(self.client)

    def start_symbol_ticker_socket(self, symbol: str) -> None:
        self.socketManager = self.get_socket_manager()
        self.socket = self.socketManager.start_symbol_ticker_socket(symbol, self.process_message)
        self.start_socket()

    def start_socket(self) -> None:
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
            self.strategy.run(msg)
