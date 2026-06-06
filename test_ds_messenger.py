# Jordan Rinne
# jrinne@uci.edu
# 16935997


from ds_messenger import DirectMessenger, DirectMessage


def test_send_message():
    messenger = DirectMessenger("127.0.0.1", "testuser", "password123")

    recipient = DirectMessenger("127.0.0.1", "testuser_2", "password123")
    recipient.retrieve_new()

    result = messenger.send("Hello from pytest!", "testuser_2")
    
    assert result is True


def test_retrieve_new():
    messenger = DirectMessenger("127.0.0.1", "testuser", "password123")
    
    new_messages = messenger.retrieve_new()

    assert isinstance(new_messages, list)


def test_retrieve_all():
    messenger = DirectMessenger("127.0.0.1", "testuser", "password123")
    
    all_messages = messenger.retrieve_all()
    
    assert isinstance(all_messages, list)

    if len(all_messages) > 0:
        assert isinstance(all_messages[0], DirectMessage)
        assert all_messages[0].message is not None
        assert all_messages[0].sender is not None
        assert all_messages[0].timestamp is not None


def test_self_send_message():

    messenger = DirectMessenger("127.0.0.1", "testuser", "password123")
    
    result = messenger.send("Hello from pytest!", "testuser")
    
    assert result is True