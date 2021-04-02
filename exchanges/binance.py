from binance.client import Client
from binance.enums import *
from binance.websockets import BinanceSocketManager
from twisted.internet import reactor

from exchanges import exchange
from models.order import Order
from models.price import Price


class Binance(exchange.Exchange):

    def __init__(self, key: str, secret: str):
        super().__init__(key, secret)
        self.client = Client(self.api_key, self.api_secret)
        self.name = self.__class__.__name__

    def get_client(self) -> Client:
        return self.client

    def get_symbol(self) -> str:
        return self.currency + self.asset

    def get_socket_manager(self) -> BinanceSocketManager:
        return BinanceSocketManager(self.client)

    def get_candle(self, interval=Client.KLINE_INTERVAL_1MINUTE):
        return self.client.get_klines(symbol=self.get_symbol(), interval=interval)

    def get_historical_candles(self, start: str, end=None, interval=Client.KLINE_INTERVAL_1MINUTE):
        for candle in self.client.get_historical_klines_generator(self.get_symbol(), interval, start, end):
            print(candle)

    def symbol_ticker(self):
        response = self.client.get_symbol_ticker(symbol=self.get_symbol())
        return Price(pair=self.get_symbol(), currency=self.currency, asset=self.asset, exchange=self.name,
                     current=response['price'])

    def start_symbol_socket(self, symbol: str):
        self.socketManager = self.get_socket_manager()
        self.socket = self.socketManager.start_symbol_ticker_socket(symbol=self.get_symbol(),
                                                                    callback=self.process_message)
        self.start_socket()

    def get_account(self):
        return self.client.get_account()

    def get_asset_balance(self, currency):
        response = self.client.get_asset_balance(currency)
        return response['free']

    def test_order(self, order: Order):
        return self.client.create_test_order(
            symbol=order.symbol,
            side=order.side,
            type=order.type,
            time_in_force=TIME_IN_FORCE_GTC,
            quantity=order.quantity,
            price=order.price
        )

    def order(self, order: Order):
        return self.client.create_order(
            symbol=order.symbol,
            side=order.side,
            type=order.type,
            time_in_force=TIME_IN_FORCE_GTC,
            quantity=order.quantity,
            price=order.price
        )

    def check_order(self, order_id):
        return self.client.get_order(
            symbol=self.get_symbol,
            order_id=order_id
        )

    def cancel_order(self, order_id):
        return self.client.cancel_order(
            symbol=self.get_symbol,
            order_id=order_id
        )

    def start_socket(self):
        print('*' * 20, 'Starting WebSocket connection', '*' * 20)
        self.socketManager.start()

    def close_socket(self):
        self.socketManager.stop_socket(self.socket)
        self.socketManager.close()
        reactor.stop()

    def process_message(self, msg):
        if msg['e'] == 'error':
            print(msg)
            self.close_socket()
        else:
            self.strategy.run(
                Price(pair=self.get_symbol(), currency=self.currency, asset=self.asset, exchange=self.name,
                      current=msg['b'], lowest=msg['l'], highest=msg['h'])
            )
