import sys

from datetime import datetime

from api.rest import Rest
from models.price import Price


class Importer:
    def __init__(self, exchange, period_start: datetime, period_end=None, interval=60, *args, **kwargs):
        self.exchange = exchange
        self.interval = interval
        self.period_start = period_start
        self.period_end = period_end
        self.start = datetime.now()
        self.rest = Rest()

    def process(self):
        for price in self.exchange.historical_symbol_ticker_candle(self.period_start, self.period_end, self.interval):
            print(self.persist(price).json())

        execution_time = datetime.now() - self.start
        print('Execution time:', str(execution_time.total_seconds()), 'seconds')
        sys.exit()

    # Persist price on internal API
    def persist(self, price: Price):
        try:
            data = price.__dict__
            data['currency'] = '/api/currencies/' + data['currency']
            data['asset'] = '/api/currencies/' + data['asset']
            data['exchange'] = '/api/exchanges/' + data['exchange']
            data['dataset'] = '/api/datasets/f06db3d5-1d29-4f2d-9b41-a785a9b429b1'
            response = self.rest.post('prices', data=data)
            return response
        except Exception as e:
            pass
