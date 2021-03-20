class Exchange:

    def __init__(self, key: str, secret: str) -> None:
        self.api_key = key
        self.api_secret = secret

        self.client = None
        self.socketManager = None
        self.socket = None
        self.symbol = None
        self.strategy = None

    def set_symbol(self, symbol: str) -> None:
        self.symbol = symbol

    def set_strategy(self, strategy) -> None:
        self.strategy = strategy
