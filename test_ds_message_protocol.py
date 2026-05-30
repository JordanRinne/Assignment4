# Jordan Rinne
# jrinne@uci.edu
# 16935997


import ds_protocol
import json


def test_direct_message():
    result = ds_protocol.direct_msg(
        token="abc123",
        recipient="recipient_user",
        entry="Direct Message Entry",
        timestamp="2024-06-01T12:00:00Z"
    )
    
    json_obj = json.loads(result)

    assert json_obj["token"] == "abc123"
    assert json_obj["directmessage"]["recipient"] == "recipient_user"
    assert json_obj["directmessage"]["entry"] == "Direct Message Entry"
    assert json_obj["directmessage"]["timestamp"] == "2024-06-01T12:00:00Z"


def test_direct_message_unread():
    result = ds_protocol.direct_msg_unread(token="abc123")
    
    json_obj = json.loads(result)

    assert json_obj["token"] == "abc123"
    assert json_obj["directmessage"] == "new"


def test_direct_message_all():
    result = ds_protocol.direct_msg_all(token="abc123")
    
    json_obj = json.loads(result)

    assert json_obj["token"] == "abc123"
    assert json_obj["directmessage"] == "all"


def test_extract_direct_msg_send_response():
    response = '''
    {
      "response": {
        "type": "ok",
        "message": "Direct message sent"
      }
    }
    '''

    result = ds_protocol.extract_json(response)

    assert result.type == 'ok'
    assert result.message == 'Direct message sent'
    assert result.token == ''
    assert result.messages == []


def test_extract_new_messages_response():
    response = '''
    {
      "response": {
        "type": "ok",
        "messages": [
          {
            "message": "hi",
            "from": "danny",
            "timestamp": "1603167689.3928561"
          },
          {
            "message": "hey",
            "from": "max",
            "timestamp": "1603167689.3928561"
          }
        ]
      }
    }
    '''

    result = ds_protocol.extract_json(response)

    assert result.type == 'ok'
    assert len(result.messages) == 2
    assert result.messages[0]['message'] == 'hi'
    assert result.messages[0]['from'] == 'danny'
    assert result.messages[1]['from'] == 'max'


def test_extract_all_messages_response():
    response = '''
    {
      "response": {
        "type": "ok",
        "messages": [
          {
            "message": "yoooooo",
            "from": "danny",
            "timestamp": "1603167689.3928561"
          },
          {
            "message": "wsp",
            "recipient": "danny",
            "timestamp": "1603167699.3928561"
          }
        ]
      }
    }
    '''

    result = ds_protocol.extract_json(response)

    assert result.type == 'ok'
    assert len(result.messages) == 2

    received = result.messages[0]
    sent = result.messages[1]

    assert received['from'] == 'danny'
    assert sent['recipient'] == 'danny'
    assert sent['message'] == 'wsp'


def test_extract_bad_json():
    result = ds_protocol.extract_json('{bad json')

    assert result.type == 'error'
    assert result.message == 'json cannot be decoded.'
    assert result.token == ''
    assert result.messages == []
