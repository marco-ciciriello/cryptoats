import signal
import sys
import threading

from decouple import config

from exchanges import binance
from strategies import debug, watcher

exchange_name = config('EXCHANGE')
mode = config('DEFAULT_MODE')
strategy = config('DEFAULT_STRATEGY')
trading_mode = config('DEFAULT_TRADING_MODE')
interval = config('DEFAULT_TRADE_CANDLESTICK_INTERVAL')
symbol = config('DEFAULT_SYMBOL')

print('*' * 20, f'Connecting to {exchange_name.upper()}', '*' * 20)
exchange = binance.Binance(config('BINANCE_API_KEY'), config('BINANCE_API_SECRET'))
exchange.set_symbol(symbol)

if strategy == 'debug':
    exchange.set_strategy(debug)


def signal_handler(signal: int, frame) -> None:
    print('\n' + '*' * 20, 'Closing WebSocket connection', '*' * 20)
    exchange.close_socket()
    sys.exit(0)


if len(sys.argv) > 1:
    symbol = sys.argv[1]

if trading_mode == 'trade':
    print('*' * 20, 'CAUTION: TRADING MODE ACTIVATED', '*' * 20)
else:
    print('Test mode')

if mode == 'watcher' or mode == 'live':
    print(f'{mode} mode on {symbol} symbol')
    if mode == 'watcher':
        exchange.set_strategy(watcher)
    exchange.start_symbol_ticker_socket(symbol)

    # Listen for keyboard interrupt event to close socket
    signal.signal(signal.SIGINT, signal_handler)
    forever = threading.Event()
    forever.wait()

if mode == 'backtest':
    period_start = config('DEFAULT_PERIOD_START')
    period_end = config('DEFAULT_PERIOD_END')
    print(f'Backtest mode on {symbol} symbol for period from {period_start} to {period_end} with {interval} candlesticks.')
    exchange.get_historical_candles(period_start, period_end, interval)
