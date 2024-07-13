"""
Module for decrypting configuration files using Fernet symmetric encryption.
"""

import json
import os
from cryptography.fernet import Fernet


class ConfigDecryptor:
    """
    Class to handle decryption of configuration files.
    """

    def __init__(self, decryption_key):
        """
        Initialize the ConfigDecryptor with a given decryption key.

        Args:
            decryption_key (bytes): The key to use for decryption.
        """
        self.decryption_key = decryption_key

    def decrypt(self):
        """
        Decrypt the 'config.enc' file and return the configuration data.

        Returns:
            dict: The decrypted configuration data.

        Raises:
            FileNotFoundError: If the 'config.enc' file does not exist.
            Exception: If any other error occurs during decryption.
        """
        if not os.path.exists("config.enc"):
            raise FileNotFoundError(
                "The encrypted configuration file 'config.enc' does not exist."
            )

        fernet = Fernet(self.decryption_key)
        with open("config.enc", "rb") as encrypted_file:
            encrypted = encrypted_file.read()
        decrypted = fernet.decrypt(encrypted).decode()
        return json.loads(decrypted)

    def hello_world(self):
        """
        Placeholder
        """
        return "Hello world"


# Define your key here
# Replace with your actual key
DECRYPTION_KEY = b"u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI="

if __name__ == "__main__":
    decryptor = ConfigDecryptor(DECRYPTION_KEY)
    try:
        config = decryptor.decrypt()
        print(config)
    except FileNotFoundError as e:
        print(e)
