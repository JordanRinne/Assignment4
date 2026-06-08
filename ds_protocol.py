# Jordan Rinne
# jrinne@uci.edu
# 16935997

import json
from collections import namedtuple

# Namedtuple to hold the values retrieved from json messages.
# TODO: update this named tuple to use DSP protocol keys
DataTuple = namedtuple('DataTuple', ['type', 'message', 'token', 'messages'])


def extract_json(json_msg: str) -> DataTuple:
    '''
    Call the json.loads function on a json string and convert
    it to a DataTuple object
    '''
    try:
        json_obj = json.loads(json_msg)
        response = json_obj.get('response', {})

        response_type = response.get('type', 'error')
        message = response.get('message', '')
        token = response.get('token', '')
        messages = response.get('messages', [])

        return DataTuple(response_type, message, token, messages)

    except json.JSONDecodeError:
        return DataTuple('error', 'json cannot be decoded.', '', [])


def join_msg(username: str, password: str) -> str:
    '''
    Create a json string with the appropriate keys
    and values to join a ds server

    :param username: The user name to be assigned to the message.
    :param password: The password associated with the username.
    '''
    message = {
        "join": {
            "username": username,
            "password": password,
            "token": ""
        }
    }
    return json.dumps(message)


# Deleted unused bio_msg and post_msg functions
# since they are not needed for the assignment.


def direct_msg(token: str, entry: str, recipient: str, timestamp: str) -> str:
    message = {
        "token": token,
        "directmessage": {
            "entry": entry,
            "recipient": recipient,
            "timestamp": timestamp
        }
    }
    return json.dumps(message)


def direct_msg_new(token: str) -> str:
    message = {
        "token": token,
        "directmessage": "new"
    }
    return json.dumps(message)


def direct_msg_all(token: str) -> str:
    message = {
        "token": token,
        "directmessage": "all"
    }
    return json.dumps(message)
