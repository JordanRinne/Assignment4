# Jordan Rinne
# jrinne@uci.edu
# 16935997


class DirectMessage:
    def __init__(self):
        self.recipient = None
        self.messages = None
        self.timestamp = None


class DirectMessenger:
    def __init__(self, dsuserver=None, username=None, password=None):
        self.token = None

    def send(self, message: str, recipient: str) -> bool:
        pass

    def retrieve_new(self) -> list:
        pass

    def retrieve_all(self) -> list:
        pass
