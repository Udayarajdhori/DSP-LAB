from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

# Helper functions for AES encryption/decryption

def pad(s):
    return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)


def unpad(s):
    return s[:-ord(s[len(s) - 1:])]


def encrypt_message(key, message):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message).encode())
    iv = base64.b64encode(cipher.iv).decode('utf-8')
    ct = base64.b64encode(ct_bytes).decode('utf-8')
    return iv + ":" + ct


def decrypt_message(key, encrypted_message):
    iv, ct = encrypted_message.split(":")
    iv = base64.b64decode(iv)
    ct = base64.b64decode(ct)
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    pt = unpad(cipher.decrypt(ct).decode())
    return pt

# Shared secret key (for demo purposes)
key = get_random_bytes(16)

# Simulated server (just forwards encrypted messages)

def server_forward(encrypted_msg):
    print("\n[Server] Forwarding encrypted message...")
    return encrypted_msg

# Simple chat loop
print("=== Secure E2EE Chat Simulation ===")
print("Type 'exit' to quit.\n")
sender = "User A"
receiver = "User B"

while True:
    msg = input(f"{sender}: ")
    if msg.lower() == 'exit':
        print("Chat ended.")
        break

    # Encrypt before sending
    encrypted_msg = encrypt_message(key, msg)
    print(f"[{sender}] Encrypted message:", encrypted_msg)

    # Server forwards message
    forwarded_msg = server_forward(encrypted_msg)

    # Receiver decrypts
    decrypted_msg = decrypt_message(key, forwarded_msg)
    print(f"{receiver} received: {decrypted_msg}\n")

    # Swap sender and receiver for next turn
    sender, receiver = receiver, sender