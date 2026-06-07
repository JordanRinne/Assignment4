# Jordan Rinne
# jrinne@uci.edu
# 16935997

import socket
import threading
import json
from pathlib import Path
import sys
from flask import Flask, render_template, redirect, url_for
from datetime import datetime
import string
import secrets

USERS_PATH = 'users.json'
POSTS_PATH = 'posts.json'
STORE_DIR_PATH = 'store'
DEBUG = True  # SET THIS TO FALSE IF YOU DONT WANT DEBUGGING OUTPUT


# The server uses two json files to store data:
# users - bio's, posts
# posts - just the posts for each user and timestamp


def generate_token():
    '''Randomly generate a token of the form
    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'''
    return (
        f'{_generate_random_string(8)}-'
        f'{_generate_random_string(4)}-'
        f'{_generate_random_string(4)}-'
        f'{_generate_random_string(4)}-'
        f'{_generate_random_string(12)}'
    )


def _generate_random_string(n: int) -> str:
    '''Generate a randm alphanumeric string of length n'''
    alphanums = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphanums) for _ in range(n))


users_file_lock = threading.Lock()
posts_file_lock = threading.Lock()


class DSUServer:

    def __init__(self, host='127.0.0.1', port=3001):
        self.host = host
        self.port = port
        self.sessions = {}  # token -> user
        self.clients = []

    def handle_client(self, client_socket, client_address):
        '''Handle requests from a single client'''
        current_user_token = None
        self.clients.append(client_socket)
        try:
            while True:
                data = client_socket.recv(4096)
                if DEBUG:
                    print(f"Message received by server: {repr(data)}")
                direct_message_read = False
                direct_message_sent = False
                msg = data.decode().strip()
                if not msg:
                    if DEBUG:
                        print("Connection closed.")
                    break
                try:
                    command = json.loads(msg.strip())
                except json.JSONDecodeError:
                    message = 'Incorrectly formatted JSON message.'
                    status = 'error'
                else:
                    message = ""
                    status = "error"

                    if 'join' in command:

                        if len(command) != 1:
                            status = "error"
                            message = "Incorrectly formatted join command."
                        elif len(command['join']) > 3:
                            status = "error"
                            message = "Extra fields provided"
                            " to join command object."
                        elif not all(
                            field in command['join'] for field in [
                                'username', 'password', 'token'
                            ]
                        ):
                            status = "error"
                            message = "Missing required fields"
                            " for join command object."
                        elif current_user_token:
                            status = "error"
                            message = "User already joined"
                            " on the active session."
                        else:
                            # execute join command

                            uname = command['join']['username']
                            password = command['join']['password']
                            token = command['join']['token']

                            fetched_user = self._get_or_create_new_user(
                                uname, password
                            )

                            current_user_token = generate_token()
                            if not fetched_user:
                                message = f'Welcome to ICS32'
                                f' Distributed Social, {uname}!'
                                status = 'ok'
                                self.sessions[current_user_token] = uname

                            else:
                                if fetched_user['password'] != password:
                                    status = "error"
                                    message = 'Incorrect password'
                                    f'for the user {uname}'
                                    current_user_token = None

                                else:
                                    status = "ok"
                                    message = f'Welcome back, {uname}!'
                                    self.sessions[current_user_token] = uname

                    elif 'bio' in command:
                        if 'token' not in command:

                            message = "Missing token."
                            status = "error"
                            # print('Missing token')
                        elif len(command) != 2:
                            message = "Incorrectly formatted bio command."
                            status = "error"
                            # print('Incorrectly formatted command')
                        elif len(command['bio']) > 2:
                            message = "Extra fields provided"
                            " to bio command object."
                            status = "error"
                            # print('Incorrect number of fields')
                        elif not all(
                            field in command['bio'] for field in [
                                'entry', 'timestamp'
                            ]
                        ):
                            status = "error"
                            message = "Missing required fields"
                            " for bio command object."

                        else:
                            entry = command['bio']['entry']
                            # timestamp = command['bio']['timestamp']

                            timestamp = str((datetime.now().timestamp()))
                            token = command['token']
                            if (
                                token == current_user_token
                                and token in self.sessions
                            ):
                                current_user = self.sessions[token]
                                self._update_bio(
                                    current_user, entry, timestamp
                                )
                                message = f"Bio for {current_user} updated."
                                status = 'ok'
                            else:
                                message = 'Invalid user token.'
                                status = 'error'

                    elif 'post' in command:
                        if 'token' not in command:
                            message = 'Missing token.'
                            status = 'error'
                        elif len(command) != 2:
                            message = "Incorrectly formatted post command."
                            status = 'error'
                        elif len(command['post']) > 2:
                            message = "Extra fields provided"
                            " to post command object."
                            status = 'error'
                        elif not all(
                            field in command['post'] for field in [
                                'entry', 'timestamp'
                            ]
                        ):
                            message = "Missing required fields"
                            " for post command."
                            status = 'error'
                        else:
                            entry = command['post']['entry']
                            # timestamp = command['post']['timestamp']

                            timestamp = str((datetime.now().timestamp()))
                            token = command['token']
                            if (
                                token == current_user_token
                                and token in self.sessions
                            ):
                                current_user = self.sessions[token]
                                self._create_post(
                                    current_user, entry, timestamp
                                )
                                message = f'Post created by {current_user}'
                                status = 'ok'
                            else:
                                message = 'Invalid user token.'
                                status = 'error'

                    # direct message handling
                    elif 'directmessage' in command:

                        args = command['directmessage']

                        if 'token' not in command:
                            message = 'Missing token.'
                            status = 'error'
                        elif len(command) != 2:
                            message = "Incorrectly formatted"
                            " directmessage command."
                            status = 'error'
                        elif (
                            args not in ['all', 'new']
                            and not (type(args) is dict and len(args) == 3)
                        ):
                            message = "Incorrect fields provided"
                            " to directmessage command object."
                            status = 'error'
                        elif type(args) is dict and not all(
                            field in command['directmessage'] for field in [
                                'entry', 'timestamp', 'recipient'
                            ]
                        ):
                            message = "Missing required fields"
                            " for directmessage command."
                            status = 'error'
                        else:
                            token = command['token']

                            if type(args) is dict:
                                recipient = args['recipient']
                                # timestamp = args['timestamp']
                                timestamp = str((datetime.now().timestamp()))
                                entry = args['entry']
                                print(token, current_user_token, self.sessions)
                                if (
                                    token == current_user_token
                                    and token in self.sessions
                                ):
                                    current_user = self.sessions[token]
                                    direct_message_sent = True

                                    if self._send_message(
                                        entry,
                                        current_user,
                                        recipient,
                                        timestamp
                                    ):
                                        message = f'Direct message sent'
                                        status = 'ok'
                                    else:
                                        message = f'Unable to'
                                        ' send direct message'
                                        status = 'error'
                                else:
                                    message = 'Invalid user token.'
                                    status = 'error'
                            elif args == 'all':
                                if (
                                    token == current_user_token
                                    and token in self.sessions
                                ):
                                    current_user = self.sessions[token]
                                    direct_message_read = True
                                    message = self._read_all_messages(
                                        current_user
                                    )
                                    status = 'ok'
                                else:
                                    message = f'Invalid user token.'
                                    status = 'error'
                            elif args == 'new':
                                if (
                                    token == current_user_token
                                    and token in self.sessions
                                ):
                                    current_user = self.sessions[token]
                                    direct_message_read = True
                                    message = self._read_new_messages(
                                        current_user
                                    )
                                    status = 'ok'
                                else:
                                    message = f'Invalid user token.'
                                    status = 'error'

                            else:
                                message = 'Invalid argument '
                                'for directmessage field.'
                                status = 'error'

                    else:
                        message = 'Invalid command.'
                        status = 'error'
                if DEBUG:
                    print(f'Server sending the following message: "{message}"')
                if direct_message_read:
                    resp = {'response': {'type': status, 'messages': message}}
                elif direct_message_sent:
                    resp = {'response': {'type': status, 'message': message}}
                elif status == 'ok':
                    resp = {
                        'response': {
                            'type': status,
                            'message': message,
                            'token': current_user_token
                        }
                    }
                else:
                    resp = {'response': {'type': status, 'message': message}}
                json_response = json.dumps(resp).encode()
                client_socket.sendall(json_response + b'\r\n')
            if current_user_token and current_user_token in self.sessions:
                del self.sessions[current_user_token]
        except Exception as e:
            print(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            self.clients.remove(client_socket)

    def _send_message(self, entry, username, recipient, timestamp=''):
        with users_file_lock:
            users_path = Path('.') / STORE_DIR_PATH / Path(USERS_PATH)
            existing_users = None
            with users_path.open('r') as user_file:
                existing_users = json.load(user_file)

            fetched_sender = existing_users.get(username, None)
            fetched_user = existing_users.get(recipient, None)
            if not fetched_sender:
                return False
            if not fetched_user:
                return False

            else:
                with users_path.open('w') as user_file:
                    fetched_sender['messages'].append(
                        {
                            'message': entry,
                            'recipient': recipient,
                            'timestamp': timestamp,
                            'status': 'sent'
                        }
                    )
                    fetched_user['messages'].append(
                        {
                            'message': entry,
                            'from': username,
                            'timestamp': timestamp,
                            'status': 'new'
                        }
                    )
                    existing_users[recipient] = fetched_user
                    existing_users[username] = fetched_sender
                    json.dump(existing_users, user_file)
        return True

    def _read_all_messages(self, username):
        with users_file_lock:
            users_path = Path('.') / STORE_DIR_PATH / Path(USERS_PATH)
            existing_users = None
            with users_path.open('r') as user_file:
                existing_users = json.load(user_file)

            fetched_user = existing_users.get(username, None)
            if not fetched_user:
                return False
            result = []
            for message in fetched_user['messages']:
                if 'from' in message:
                    mod_message = {
                        'from': message['from'],
                        'message': message['message'],
                        'timestamp': message['timestamp']
                    }
                else:
                    mod_message = {
                        'recipient': message['recipient'],
                        'message': message['message'],
                        'timestamp': message['timestamp']
                    }
                result.append(mod_message)
                if message['status'] == 'new':
                    message['status'] = 'read'

            else:
                with users_path.open('w') as user_file:

                    existing_users[username] = fetched_user
                    json.dump(existing_users, user_file)

            return sorted(result, key=lambda x: float(x["timestamp"]))

    def _read_new_messages(self, username):
        with users_file_lock:
            users_path = Path('.') / STORE_DIR_PATH / Path(USERS_PATH)
            existing_users = None
            with users_path.open('r') as user_file:
                existing_users = json.load(user_file)

            fetched_user = existing_users.get(username, None)
            if not fetched_user:
                return False
            result = []
            for message in fetched_user['messages']:
                if message['status'] == 'new':
                    mod_message = {
                        'from': message['from'],
                        'message': message['message'],
                        'timestamp': message['timestamp']
                    }
                    result.append(mod_message)
                    message['status'] = 'read'

            else:
                with users_path.open('w') as user_file:
                    existing_users[username] = fetched_user

                    json.dump(existing_users, user_file)

            return sorted(result, key=lambda x: float(x["timestamp"]))

    def _get_user(self, username):
        '''Gets the user object associated with the username.
        This function is never called.'''
        with users_file_lock:
            users_path = Path('.') / STORE_DIR_PATH / Path(USERS_PATH)
            with users_path.open('r') as user_file:
                existing_users = json.load(user_file)
                fetched_user = existing_users.get(username, None)
                return fetched_user

    def _get_or_create_new_user(self, username, password):

        '''Read from the user file and get the username associated
        with the username. If it doesnt exist, create a new user.'''
        with users_file_lock:
            users_path = Path('.') / STORE_DIR_PATH / Path(USERS_PATH)
            existing_users = None
            with users_path.open('r') as user_file:
                existing_users = json.load(user_file)

            fetched_user = existing_users.get(username, None)
            if fetched_user:
                return fetched_user
            else:
                with users_path.open('w') as user_file:

                    fetched_user = existing_users.get(username, None)
                    if fetched_user:
                        return False
                    else:
                        existing_users.update(
                            {
                                username: {
                                    'password': password,
                                    'bio': {"entry": "", "timestamp": ""},
                                    'posts': [],
                                    'messages': []
                                }
                            }
                        )
                    json.dump(existing_users, user_file)

    def _update_bio(self, username, entry, timestamp):

        '''Update the bio associated with the username.'''
        with users_file_lock:
            users_path = Path('.') / STORE_DIR_PATH / Path(USERS_PATH)
            existing_users = None
            with users_path.open('r') as user_file:
                existing_users = json.load(user_file)

            fetched_user = existing_users.get(username, None)
            with users_path.open('w') as user_file:

                fetched_user = existing_users.get(username, None)
                if not fetched_user:
                    return False
                else:
                    fetched_user['bio'] = {
                        'entry': entry, 'timestamp': timestamp
                    }

                json.dump(existing_users, user_file)

    def _create_post(self, username, entry, timestamp):
        '''Create a post for the user (username). Add the post
        to the user's posts and add the post to the list of all posts'''
        with users_file_lock:
            users_path = Path('.') / STORE_DIR_PATH / Path(USERS_PATH)
            existing_users = None
            with users_path.open('r') as user_file:
                existing_users = json.load(user_file)

            fetched_user = existing_users.get(username, None)

            with users_path.open('w') as user_file:
                fetched_user = existing_users.get(username, None)
                if not fetched_user:
                    return False
                else:
                    fetched_user['posts'].insert(
                        0,
                        {
                            'user': username,
                            'entry': entry,
                            'timestamp': timestamp
                        }
                    )

                json.dump(existing_users, user_file)
        with posts_file_lock:
            existing_posts = None
            posts_path = Path('.') / STORE_DIR_PATH / Path(POSTS_PATH)
            with posts_path.open('r') as posts_file:
                existing_posts = json.load(posts_file)['posts']

            existing_posts.insert(
                0, {'user': username, 'entry': entry, 'timestamp': timestamp}
            )

            with posts_path.open('w') as posts_file:
                json.dump({"posts": existing_posts}, posts_file)

    def _create_storage_system(self):
        '''Creates the local storage system if it doesnt already exist.
        Will create a directory called "store" with two files posts.json
        and users.json'''
        users_path = Path('.') / STORE_DIR_PATH / Path(USERS_PATH)
        posts_path = Path('.') / STORE_DIR_PATH / Path(POSTS_PATH)
        store_path = Path('.') / Path(STORE_DIR_PATH)
        store_path.mkdir(exist_ok=True)
        if not users_path.exists():
            with users_path.open('w') as json_file:
                json.dump({}, json_file, indent=4)
        if not posts_path.exists():
            with posts_path.open('w') as json_file:
                json.dump({'posts': []}, json_file, indent=4)

    def start_server(self):
        '''Starts the server (hence the name of the method :))'''
        self._create_storage_system()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
                srv.bind((self.host, self.port))
                srv.listen(5)
                if DEBUG:
                    print("DSUserver is listening on port", self.port)
                while True:
                    connection, address = srv.accept()
                    client_handler = threading.Thread(
                        target=self.handle_client, args=(connection, address)
                    )
                    client_handler.start()
        except KeyboardInterrupt as e:
            if DEBUG:
                print(f'Server shutting down...')
        finally:
            for conn in self.clients:
                conn.close()
            self.clients = []
            if DEBUG:
                print('Disconnected all clients.')


app = Flask(__name__)


@app.route('/')
def index():
    # Display the latest messages from the TCP server in the browser
    return redirect(url_for('posts'))


@app.route('/posts')
def posts():
    with posts_file_lock:
        existing_posts = None
        posts_path = Path('.') / STORE_DIR_PATH / Path(POSTS_PATH)
        with posts_path.open('r') as posts_file:
            existing_posts = json.load(posts_file)['posts']

    return render_template('index.html', posts=existing_posts)


@app.route('/user/<string:username>')
def user_profile(username):
    with users_file_lock:
        users_path = Path('.') / STORE_DIR_PATH / Path(USERS_PATH)
        existing_users = None
        with users_path.open('r') as user_file:
            existing_users = json.load(user_file)

        fetched_user = existing_users.get(username, None)
        # print(fetched_user['posts'])
        if fetched_user:
            user = {
                'username': username,
                'bio': fetched_user['bio']['entry'],
                'biots': fetched_user['bio']['timestamp'],
                'posts': fetched_user['posts']
            }
            return render_template('user_profile.html', user=user)
        else:
            return "User not found..."


def run_flask_server(host='127.0.0.1', port=3002):
    app.run(host=host, port=port)


def run_servers(host='127.0.0.1', port1=3001, port2=3002):

    flask_thread = threading.Thread(
        target=run_flask_server, daemon=True, args=(host, port2)
    )
    flask_thread.start()

    try:
        server = DSUServer(host, port1)
        server.start_server()
    except Exception as e:
        print(f'Server raised the following error:{e}')


if __name__ == '__main__':
    host = '127.0.0.1'
    port1 = 3001
    port2 = 3002
    if len(sys.argv) >= 2:
        port1 = int(sys.argv[1])
    if len(sys.argv) >= 3:
        port2 = int(sys.argv[2])

    run_servers(host, port1, port2)
