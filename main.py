import signal
import sys
import threading

from decouple import config

from exchanges import binance, coinbase
from strategies import debug, watcher

exchange_name = config('DEFAULT_EXCHANGE')
exchanges = config('EXCHANGES').split(',')
mode: str = config('DEFAULT_MODE')
strategy: str = config('DEFAULT_STRATEGY')
trading_mode: str = config('DEFAULT_TRADING_MODE')
interval: str = config('DEFAULT_TRADE_CANDLESTICK_INTERVAL')
currency: str = config('DEFAULT_CURRENCY')
asset: str = config('DEFAULT_ASSET')

# Connect to exchange
print('*' * 20, f'Connecting to {exchange_name.upper()}', '*' * 20)
if exchange_name == 'binance':
    exchange = binance.Binance(config('BINANCE_API_KEY'), config('BINANCE_API_SECRET'))
if exchange_name == 'coinbase':
    exchange = coinbase.Coinbase(config('COINBASE_API_KEY'), config('COINBASE_API_SECRET'))


# Parse symbol pair from first command argument
if len(sys.argv) > 1:
    symbol = sys.argv[1].split('_')
    if len(symbol) > 1:
        currency = symbol[0]
        asset = symbol[1]

exchange.set_currency(currency)
exchange.set_asset(asset)

if strategy == 'debug':
    exchange.set_strategy(debug)


def signal_handler(signal: int, frame) -> None:
    print('\n' + '*' * 20, 'Closing WebSocket connection', '*' * 20)
    exchange.close_socket()
    sys.exit(0)


if trading_mode == 'real':
    print('*' * 20, 'CAUTION: TRADING MODE ACTIVATED', '*' * 20)
else:
    print('Test mode')

if mode == 'watcher' or mode == 'live':
    print(f'{mode} mode on {exchange.get_symbol()} symbol')

    if mode == 'watcher':
        exchange.set_strategy(watcher)

    exchange.start_symbol_socket(exchange.get_symbol())

    # Listen for keyboard interrupt event to close socket
    signal.signal(signal.SIGINT, signal_handler)
    forever = threading.Event()
    forever.wait()

if mode == 'backtest':
    period_start = config('DEFAULT_PERIOD_START')
    period_end = config('DEFAULT_PERIOD_END')
    print(f'Backtest mode on {symbol} symbol for period from {period_start} to {period_end} with {interval} candlesticks.')
    exchange.get_historical_candles(period_start, period_end, interval)
