from datetime import datetime


class AbstractModel:

    created = datetime.now()

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            print(f'{key} is {value}')
            setattr(self, key, value)
