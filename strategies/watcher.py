from models import price


def run(new_price: price.Price):
    print('*' * 20)
    print('Exchange: ', new_price.exchange)
    print('Pair: ', new_price.pair)
    print('Price: ', new_price.current)
