from cryptography.fernet import Fernet

def generate_key():
    """Generates a key for encryption."""
    return Fernet.generate_key()

def encrypt_message(key, message):
    """Encrypts a message using the provided key."""
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message

def decrypt_message(key, encrypted_message):
    """Decrypts a message using the provided key."""
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message).decode()
    return decrypted_message
