
# LICENSE
# This software is the exclusive property of Gencovery SAS. 
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import os
from cryptography.fernet import Fernet

__cdir__ = os.path.dirname(os.path.abspath(__file__))
secret_file_path = os.path.join(__cdir__, "../.secret.key")


def generate_key():
    """
    Generates a key and save it into a file
    """
    key = Fernet.generate_key()
    with open(secret_file_path, "wb") as f:
        f.write(key)

def load_key():
    """
    Load the previously generated key
    """
    return open(secret_file_path, "rb").read()

def encrypt_message(message):
    """
    Encrypts a message
    """
    if not os.path.exists(secret_file_path):
        generate_key()

    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)
    return encrypted_message.decode()


def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message.encode())
    return decrypted_message.decode()
