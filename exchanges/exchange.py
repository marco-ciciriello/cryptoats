class Exchange:

    def __init__(self, key: str, secret: str):
        self.api_key = key
        self.api_secret = secret

        self.client = None
        self.socketManager = None
        self.socket = None
