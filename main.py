import importlib
import signal
import sys
import threading

from decouple import config

from models.dataset import Dataset
from services.importer import Importer

exchange_name = config('EXCHANGE')
exchanges = config('EXCHANGES').split(',')
mode: str = config('MODE')
strategy: str = config('STRATEGY')
trading_mode: str = config('TRADING_MODE')
interval: int = int(config('CANDLESTICK_INTERVAL'))
currency: str = config('CURRENCY')
asset: str = config('ASSET')

if trading_mode == 'real':
    print('*' * 20, 'CAUTION: TRADING MODE ACTIVATED', '*' * 20)
else:
    print('*' * 20, 'Test mode', '*' * 20)

# Parse symbol pair from first command argument
if len(sys.argv) > 1:
    currencies = sys.argv[1].split('_')
    if len(currencies) > 1:
        currency = currencies[0]
        asset = currencies[1]

# Load exchange
print('*' * 20, f'Connecting to {exchange_name.upper()}', '*' * 20)
exchange_module = importlib.import_module('exchanges.' + exchange_name, package=None)
exchange_class = getattr(exchange_module, exchange_name[0].upper() + exchange_name[1:])
exchange = exchange_class(config(exchange_name.upper()+'_API_KEY'), config(exchange_name.upper()+'_API_SECRET'))

# Load strategy
strategy_module = importlib.import_module('strategies.' + strategy, package=None)
strategy_class = getattr(strategy_module, strategy[0].upper() + strategy[1:])
exchange.set_strategy(strategy_class(exchange, interval))

# Load currencies
exchange.set_currency(currency)
exchange.set_asset(asset)

# Mode
print(f'{mode} mode on {exchange.get_symbol()} symbol')

if mode == 'trade':
    exchange.strategy.start()

elif mode == 'live':
    exchange.start_symbol_ticker_socket(exchange.get_symbol())

elif mode == 'backtest':
    period_start = config('PERIOD_START')
    period_end = config('PERIOD_END')
    print(f'Backtest mode on {exchange.get_symbol()} symbol for period from {period_start} to {period_end} with \
          {interval} second candlesticks.')

    # Try to find dataset
    dataset = Dataset().read({'exchange': exchange.name, 'currency': currency.lower(), 'asset': asset.lower(),
                              'period_start': period_start, 'period_end': period_end, 'interval': interval})

    print(dataset)

    if dataset.prices:
        print('Dataset found.')
        for price in dataset.prices:
            newPrice = price.populate([price])
            exchange.strategy.set_price(newPrice)
            exchange.strategy.run()
    else:
        print(f'Dataset not found, external API call to {exchange.name}.')
        for price in exchange.historical_symbol_ticker_candle(period_start, period_end, interval):
            exchange.strategy.set_price(price)
            exchange.strategy.run()

    sys.exit()

elif mode == 'import':
    period_start = config('PERIOD_START')
    period_end = config('PERIOD_END')
    print(f'Import mode on {exchange.get_symbol()} symbol for period from {period_start} to {period_end} with \
          {interval} second candlesticks.')
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


# Listen for keyboard interrupt event
signal.signal(signal.SIGINT, signal_handler)
forever = threading.Event()
forever.wait()
