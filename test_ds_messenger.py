# Jordan Rinne
# jrinne@uci.edu
# 16935997

import json
from unittest.mock import patch, MagicMock
from ds_messenger import DirectMessenger, DirectMessage


def test_convert_messages_received():
    messenger = DirectMessenger(username="my_user")
    fake_messages = [
        {"message": "hello", "from": "friend", "timestamp": "12345"}
    ]

    result = messenger._convert_messages(fake_messages)

    assert len(result) == 1
    assert result[0].message == "hello"
    assert result[0].sender == "friend"
    assert result[0].direction == "received"


def test_convert_messages_sent():
    messenger = DirectMessenger(username="my_user")
    fake_messages = [
        {"message": "hi back", "recipient": "friend", "timestamp": "12346"}
    ]

    result = messenger._convert_messages(fake_messages)

    assert len(result) == 1
    assert result[0].message == "hi back"
    assert result[0].sender == "my_user"
    assert result[0].recipient == "friend"
    assert result[0].direction == "sent"


def test_convert_messages_missing_keys():
    messenger = DirectMessenger()
    fake_messages = [{"message": "ghost message", "timestamp": "0"}]

    result = messenger._convert_messages(fake_messages)

    assert len(result) == 1
    assert result[0].sender is None


@patch.object(DirectMessenger, '_send_request')
def test_send_success(mock_send_request):
    mock_resp = MagicMock()
    mock_resp.type = 'ok'
    mock_send_request.return_value = mock_resp

    messenger = DirectMessenger()
    assert messenger.send("Hello", "friend") is True


@patch.object(DirectMessenger, '_send_request')
def test_send_fail_error(mock_send_request):
    mock_resp = MagicMock()
    mock_resp.type = 'error'
    mock_resp.message = 'Invalid token'
    mock_send_request.return_value = mock_resp

    messenger = DirectMessenger()
    assert messenger.send("Hello", "friend") is False


@patch.object(DirectMessenger, '_send_request')
def test_send_fail_none(mock_send_request):
    mock_send_request.return_value = None
    messenger = DirectMessenger()
    assert messenger.send("Hello", "friend") is False


@patch.object(DirectMessenger, '_send_request')
def test_retrieve_new_success(mock_send_request):
    mock_resp = MagicMock()
    mock_resp.type = 'ok'
    mock_resp.messages = [{"message": "yo", "from": "friend"}]
    mock_send_request.return_value = mock_resp

    messenger = DirectMessenger()
    result = messenger.retrieve_new()
    assert len(result) == 1
    assert result[0].message == "yo"


@patch.object(DirectMessenger, '_send_request')
def test_retrieve_new_fail(mock_send_request):
    mock_send_request.return_value = None
    messenger = DirectMessenger()
    assert messenger.retrieve_new() == []


@patch.object(DirectMessenger, '_send_request')
def test_retrieve_all_success(mock_send_request):
    mock_resp = MagicMock()
    mock_resp.type = 'ok'
    mock_resp.messages = [{"message": "history", "from": "friend"}]
    mock_send_request.return_value = mock_resp

    messenger = DirectMessenger()
    result = messenger.retrieve_all()
    assert len(result) == 1


@patch.object(DirectMessenger, '_send_request')
def test_retrieve_all_fail(mock_send_request):
    mock_resp = MagicMock()
    mock_resp.type = 'error'
    mock_send_request.return_value = mock_resp

    messenger = DirectMessenger()
    assert messenger.retrieve_all() == []


@patch('socket.socket')
def test_send_request_success(mock_socket_class):
    mock_socket = mock_socket_class.return_value.__enter__.return_value
    mock_file = MagicMock()
    mock_socket.makefile.return_value = mock_file

    mock_file.readline.side_effect = [
        '{"response": {"type": "ok", "message":'
        ' "Joined", "token": "token123"}}\n',
        '{"response": {"type": "ok", "message": "Action successful"}}\n'
    ]

    messenger = DirectMessenger("1.1.1.1", "usr", "pass")

    dummy_request = json.dumps({"entry": "test"})
    result = messenger._send_request(dummy_request)

    assert result.type == 'ok'
    assert result.message == 'Action successful'


@patch('socket.socket')
def test_send_request_join_fail(mock_socket_class):
    mock_socket = mock_socket_class.return_value.__enter__.return_value
    mock_file = MagicMock()
    mock_socket.makefile.return_value = mock_file

    mock_file.readline.return_value = '{"response": ' \
        '{"type": "error", "message": "Bad password"}}\n'

    messenger = DirectMessenger("1.1.1.1", "usr", "pass")
    result = messenger._send_request('{"entry": "test"}')

    assert result is None


@patch('socket.socket')
def test_send_request_exception(mock_socket_class):
    mock_socket_class.side_effect = Exception("Connection refused!")

    messenger = DirectMessenger("1.1.1.1", "usr", "pass")
    result = messenger._send_request('{"entry": "test"}')

    assert result is None
