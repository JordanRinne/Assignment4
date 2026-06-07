# Jordan Rinne
# jrinne@uci.edu
# 16935997

import time
from ds_messenger import DirectMessenger

print("Connecting as testuser2...")
# Initialize the messenger as the "other" user
messenger = DirectMessenger("127.0.0.1", "testuser2", "password123")

# Send a message to your main account
message_text = f"Hello from the test script! The time is {time.time()}"
recipient = "testuser"

print(f"Sending message to '{recipient}'...")
success = messenger.send(message_text, recipient)

if success:
    print("Message successfully sent to the server!")
else:
    print("Failed to send message.")
