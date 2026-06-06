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
        self.message = None
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

        timestamp = str(time.time())
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
        if not self._ensure_token():
            return []
        
        request = ds_protocol.direct_msg_new(
            token=self.token
        )
        response = self._send_request(request)

        if response is None or response.type != 'ok':
            return []
        
        return self._convert_messages(response.messages)


    def retrieve_all(self) -> list:
        if not self._ensure_token():
            return []
        
        request = ds_protocol.direct_msg_all(
            token=self.token
        )
        response = self._send_request(request)

        if response is None or response.type != 'ok':
            return []
        
        return self._convert_messages(response.messages)


    def _ensure_token(self) -> bool:
        if self.token is not None:
            return True
        
        return self._join()
    

    def _join(self) -> bool:
        if not self.dsuserver or not self.username or not self.password:
            return False

        request = ds_protocol.join_msg(self.username, self.password)
        response = self._send_request(request)

        if response is None:
            return False

        if response.type == 'ok' and response.token:
            self.token = response.token
            return True

        return False
    

    def _send_request(self, request: str):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.dsuserver, PORT))
                s.sendall(request.encode())
                
                f = s.makefile('r')
                response = f.read()

                return ds_protocol.extract_json(response)

        except Exception as ex:
            print(f"Error sending request: {ex}")
            return None
        
    
    def _convert_messages(self, messages: list) -> list:
        direct_messages = []

        for msg in messages:
            direct_msg = DirectMessage()
            direct_msg.message = msg.get('message', '')
            direct_msg.timestamp = msg.get('timestamp', '')

            if 'from' in msg:
                direct_msg.sender = msg.get('from')
                direct_msg.recipient = msg.get('from')
                direct_msg.direction = 'received'

            elif 'recipient' in msg:
                direct_msg.sender = self.username
                direct_msg.recipient = msg.get('recipient')
                direct_msg.direction = 'sent'

            direct_messages.append(direct_msg)

        return direct_messages
