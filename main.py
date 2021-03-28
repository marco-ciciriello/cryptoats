import signal
import sys
import threading

from decouple import config

from exchanges import binance, coinbase, coingecko, exchange
from strategies import arbitrage, debug, watcher

exchange_name = config('DEFAULT_EXCHANGE')
exchanges = config('EXCHANGES').split(',')
mode: str = config('DEFAULT_MODE')
strategy: str = config('DEFAULT_STRATEGY')
trading_mode: str = config('DEFAULT_TRADING_MODE')
interval: int = int(config('DEFAULT_TRADE_CANDLESTICK_INTERVAL'))
currency: str = config('DEFAULT_CURRENCY')
asset: str = config('DEFAULT_ASSET')

# Parse symbol pair from first command argument
if len(sys.argv) > 1:
    symbol = sys.argv[1].split('_')
    if len(symbol) > 1:
        currency = symbol[0]
        asset = symbol[1]

if trading_mode == 'real':
    print('*' * 20, 'CAUTION: TRADING MODE ACTIVATED', '*' * 20)
else:
    print('*' * 20, 'Test mode', '*' * 20)

# Connect to exchange
print('*' * 20, f'Connecting to {exchange_name.upper()}', '*' * 20)
if exchange_name == 'binance':
    exchange = binance.Binance(config('BINANCE_API_KEY'), config('BINANCE_API_SECRET'))
if exchange_name == 'coinbase':
    exchange = coinbase.Coinbase(config('COINBASE_API_KEY'), config('COINBASE_API_SECRET'))
if exchange_name == 'coingecko':
    exchange = coingecko.Coingecko(config('COINGECKO_API_KEY'), config('COINGECKO_API_SECRET'))

exchange.set_currency(currency)
exchange.set_asset(asset)

# Load strategy
if strategy == 'debug':
    exchange.set_strategy(debug.Debug(exchange, interval))

if strategy == 'watcher':
    exchange.set_strategy(watcher.Watcher(exchange, interval))

if strategy == 'arbitrage':
    exchange.set_strategy(arbitrage.Arbitrage(exchange, interval))

# Start mode
print(f'{mode} mode on {exchange.get_symbol()} symbol')

if mode == 'trader':
    exchange.strategy.start()

elif mode == 'live':
    exchange.start_symbol_ticker_socket(exchange.get_symbol())

elif mode == 'backtest':
    period_start = config('DEFAULT_PERIOD_START')
    period_end = config('DEFAULT_PERIOD_END')
    print(f'Backtest mode on {symbol} symbol for period from {period_start} to {period_end} with {interval} candlesticks.')
    exchange.get_historical_candles(period_start, period_end, interval)

else:
    print('Mode unsupported')


def signal_handler(signal: int, frame) -> None:
    if exchange.socket:
        print('\n' + '*' * 20, 'Closing WebSocket connection', '*' * 20)
        exchange.close_socket()
        sys.exit(0)
    else:
        print('\n' + '*' * 20, 'Stopping strategy', '*' * 20)
        exchange.strategy.stop()
        sys.exit(0)


# Listen for keyboard interrupt event to close socket
signal.signal(signal.SIGINT, signal_handler)
forever = threading.Event()
forever.wait()



