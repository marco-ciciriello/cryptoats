import signal
import sys
import threading

from binance.client import Client
from binance.websockets import BinanceSocketManager
from decouple import config
from strategies.margin import strat
from twisted.internet import reactor

client = Client(config('BINANCE_API_KEY'), config('BINANCE_API_SECRET'))
symbol = config('DEFAULT_SYMBOL')


def process_message(msg: dict) -> None:
    if msg['e'] == 'error':
        print(msg)
        close_socket()
    else:
        strat(msg)


def signal_handler(signal: int, frame: signal.frame) -> None:
    print('\n' + '*' * 20, 'Closing WebSocket connection', '*' * 20)
    print(type(frame))
    close_socket()
    sys.exit(0)


def close_socket() -> None:
    bm.stop_socket(conn_key)
    bm.close()
    reactor.stop()


if len(sys.argv) > 1:
    symbol = sys.argv[1]

print('*' * 20, f'Watch price for {symbol}', '*' * 20)

# Create manager
bm = BinanceSocketManager(client)

# Start symbol ticker socket
conn_key = bm.start_symbol_ticker_socket(symbol, process_message)

# Start the socket manager
bm.start()

# Listen for keyboard interrupt event
signal.signal(signal.SIGINT, signal_handler)
forever = threading.Event()
forever.wait()
