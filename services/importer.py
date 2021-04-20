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
        self.dataset = self.persist_dataset()

    def process(self):
        for price in self.exchange.historical_symbol_ticker_candle(self.period_start, self.period_end, self.interval):
            print(self.persist(price).json())

        execution_time = datetime.now() - self.start
        print('Execution time:', str(execution_time.total_seconds()), 'seconds')
        sys.exit()

    # Persist price on internal API
    def persist_price(self, price: Price):
        try:
            data = price.__dict__
            data['currency'] = '/api/currencies/' + data['currency']
            data['asset'] = '/api/currencies/' + data['asset']
            data['exchange'] = '/api/exchanges/' + data['exchange']
            data['dataset'] = '/api/datasets/' + self.dataset.uuid
            response = self.rest.post('prices', data=data)
            return response
        except Exception as e:
            pass

    # Persist dataset on internal API
    def persist_dataset(self):
        try:
            data = {'currency': '/api/currencies/' + self.exchange.currency,
                    'asset': '/api/currencies/' + self.exchange.asset,
                    'exchange': '/api/exchanges/' + self.exchange.name,
                    'periodStart': self.period_start,
                    'periodEnd': self.period_end}
            response = self.rest.post('datasets', data=data)
            return response
        except Exception as e:
            pass
