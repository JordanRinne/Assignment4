# Jordan Rinne
# jrinne@uci.edu
# 16935997

import socket
import ds_protocol
import time


PORT = 3001


class DirectMessage:
    def __init__(self):
        self.recipient = None
        self.messages = None
        self.timestamp = None
        self.sender = None
        self.direction = None


class DirectMessenger:
    def __init__(self, dsuserver=None, username=None, password=None):
        self.dsuserver = dsuserver
        self.username = username
        self.password = password
        self.token = None

    def send(self, message: str, recipient: str) -> bool:

        if not self._ensure_token():
            return False

        timestamp = time.time()
        request = ds_protocol.direct_msg(
            token=self.token,
            entry=message,
            recipient=recipient,
            timestamp=timestamp
        )
        response = self._send_request(request)

        if response is None:
            return False
        
        return response.type == 'ok'


    def retrieve_new(self) -> list:
        pass

    def retrieve_all(self) -> list:
        pass
