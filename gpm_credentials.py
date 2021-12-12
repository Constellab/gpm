# LICENSE
# This software is the exclusive property of Gencovery SAS.
# The use and distribution of this software is prohibited without the prior consent of Gencovery SAS.
# About us: https://gencovery.com

import json
import os
import urllib

from cryptography.fernet import Fernet

__cdir__ = os.path.dirname(os.path.abspath(__file__))


class CREDENTIALS():
    PUBLIC_FILE = os.path.join(__cdir__, "./.public.json")
    KEY_FILE = os.path.join(__cdir__, "./.key.pub")

    # -- D --

    @classmethod
    def decrypt_message(cls, encrypted_message):
        """
        Decrypts an encrypted message
        """
        key = cls.load_key()
        f = Fernet(key)
        decrypted_message = f.decrypt(encrypted_message.encode())
        return decrypted_message.decode()

    # -- E --

    @classmethod
    def encrypt_message(cls, message):
        """
        Encrypts a message
        """
        if not os.path.exists(cls.KEY_FILE):
            cls.generate_key()

        key = cls.load_key()
        encoded_message = message.encode()
        f = Fernet(key)
        encrypted_message = f.encrypt(encoded_message)
        return encrypted_message.decode()

    # -- G --

    @classmethod
    def generate_key(cls):
        """
        Generates a key and save it into a file
        """
        key = Fernet.generate_key()
        with open(cls.KEY_FILE, "wb") as f:
            f.write(key)

    @classmethod
    def get_git_credentials(cls):
        if os.path.exists(cls.PUBLIC_FILE):
            with open(cls.PUBLIC_FILE, 'r', encoding="utf-8") as f:
                private = json.load(f)
        else:
            raise Exception(f"File {cls.PUBLIC_FILE} not found")
        git_user = private["git"]["login"]
        git_pwd = private["git"]["credentials"]
        if not git_pwd:
            raise Exception("The invalid git password")
        elif len(git_pwd) < 64:
            git_pwd = cls.encrypt_message(git_pwd)
            private["git"]["credentials"] = git_pwd
            with open(cls.PUBLIC_FILE, 'w', encoding="utf-8") as f:
                json.dump(private, f, indent=4)
        else:
            git_pwd = cls.decrypt_message(git_pwd)
        git_pwd = urllib.parse.quote(git_pwd)
        return git_user, git_pwd

    # -- L --

    @classmethod
    def load_key(cls):
        """
        Load the previously generated key
        """
        return open(cls.KEY_FILE, "rb").read()
