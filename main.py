import signal
import sys
import threading

from decouple import config
from exchanges import binance

symbol = config('DEFAULT_SYMBOL')

exchange = binance.Binance(config('BINANCE_API_KEY'), config('BINANCE_API_SECRET'))
client = exchange.get_client()


def signal_handler(signal: int, frame) -> None:
    print('\n' + '*' * 20, 'Closing WebSocket connection', '*' * 20)
    exchange.close_socket()
    sys.exit(0)


if len(sys.argv) > 1:
    symbol = sys.argv[1]

# Open socket for symbol
print('*' * 20, f'Watch price for {symbol}', '*' * 20)
exchange.start_symbol_ticker_socket(symbol)

# Listen for keyboard interrupt event to close socket
signal.signal(signal.SIGINT, signal_handler)
forever = threading.Event()
forever.wait()
