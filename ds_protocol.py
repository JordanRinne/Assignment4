# Jordan Rinne
# jrinne@uci.edu
# 16935997

import json
from collections import namedtuple

# Namedtuple to hold the values retrieved from json messages.
# TODO: update this named tuple to use DSP protocol keys
DataTuple = namedtuple('DataTuple', ['type', 'message', 'token'])


def extract_json(json_msg: str) -> DataTuple:
    '''
    Call the json.loads function on a json string and convert
    it to a DataTuple object

    TODO: replace the pseudo placeholder keys with actual
    DSP protocol keys
    '''
    try:
        json_obj = json.loads(json_msg)
        response = json_obj['response']
        response_type = response['type']
        message = response.get('message', '')
        token = response.get('token', '')

    except json.JSONDecodeError:
        print("Json cannot be decoded.")

    return DataTuple(response_type, message, token)


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


def post_msg(token: str, entry: str, timestamp: str) -> str:
    '''
    Create a json string with the appropriate keys
    and values to post a message to a ds server

    :param token: The token associated with the user.
    :param entry: The entry to be sent to the server.
    :param timestamp: The timestamp associated with the entry.
    '''

    message = {
        "token": token,
        "post": {
            "entry": entry,
            "timestamp": timestamp
        }
    }
    return json.dumps(message)


def bio_msg(token: str, entry: str, timestamp: str) -> str:
    '''
    Create a json string with the appropriate keys
    and values to update a bio on a ds server

    :param token: The token associated with the user.
    :param entry: The entry to be updated on the server.
    :param timestamp: The timestamp associated with the entry.
    '''

    message = {
        "token": token,
        "bio": {
            "entry": entry,
            "timestamp": timestamp
        }
    }
    return json.dumps(message)
