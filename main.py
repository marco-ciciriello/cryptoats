import signal
import sys
import threading

from decouple import config

from exchanges import binance, coinbase, coingecko, exchange
from services.importer import Importer
from strategies import arbitrage, debug, logger, runner

exchange_name = config('EXCHANGE')
exchanges = config('EXCHANGES').split(',')
mode: str = config('MODE')
strategy: str = config('STRATEGY')
trading_mode: str = config('TRADING_MODE')
interval: int = int(config('CANDLESTICK_INTERVAL'))
currency: str = config('CURRENCY')
asset: str = config('ASSET')

# Parse symbol pair from first command argument
if len(sys.argv) > 1:
    currencies = sys.argv[1].split('_')
    if len(currencies) > 1:
        currency = currencies[0]
        asset = currencies[1]

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

elif strategy == 'arbitrage':
    exchange.set_strategy(arbitrage.Arbitrage(exchange, interval))

elif strategy == 'logger':
    exchange.set_strategy(logger.Logger(exchange, interval))

elif strategy == 'runner':
    exchange.set_strategy(runner.Runner(exchange, interval))

else:
    print('Strategy not found')

# Start mode
print(f'{mode} mode on {exchange.get_symbol()} symbol')

if mode == 'trade':
    exchange.strategy.start()

elif mode == 'live':
    exchange.start_symbol_ticker_socket(exchange.get_symbol())

elif mode == 'backtest':
    period_start = config('PERIOD_START')
    period_end = config('PERIOD_END')
    print(f'Backtest mode on {exchange.get_symbol()} symbol for period from {period_start} to {period_end} with {interval} second candlesticks.')
    exchange.backtest(period_start, period_end, interval)

elif mode == 'import':
    period_start = config('PERIOD_START')
    period_end = config('PERIOD_END')
    print(f'Import mode on {exchange.get_symbol()} symbol for period from {period_start} to {period_end} with {interval} second candlesticks.')
    importer = Importer(exchange, period_start, period_end, interval)
    importer.process()

else:
    print('Mode not found')


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



