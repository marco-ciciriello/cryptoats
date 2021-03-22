from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import price

db = create_engine(config('DATABASE_URL'))

Session = sessionmaker(db)
session = Session()


def run(new_price: price.Price):
    print('Symbol: ', new_price.pair, 'Price: ', new_price.curr)

    # Persist price
    session.add(new_price)
    session.commit()
