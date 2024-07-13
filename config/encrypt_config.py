"""
Module for encrypting configuration files using Fernet symmetric encryption.
"""

from cryptography.fernet import Fernet


class ConfigEncryptor:
    """
    Class to handle encryption of configuration data.
    """

    def __init__(self):
        """
        Initialize the ConfigEncryptor with a generated encryption key.
        """
        self.key = Fernet.generate_key()

    def encrypt_config(self, data):
        """
        Encrypt the configuration data and save it to 'config.enc'.

        Args:
            data (str): The configuration data to be encrypted.
        """
        fernet = Fernet(self.key)
        encrypted = fernet.encrypt(data.encode())
        with open("config.enc", "wb") as encrypted_file:
            encrypted_file.write(encrypted)

    def get_key(self):
        """
        Get the generated encryption key.

        Returns:
            str: The generated encryption key as a string.
        """
        return self.key.decode()


if __name__ == "__main__":
    CONFIG_DATA = """
    {
        "url": "https://yourstore.com",
        "consumer_key": "ck_yourconsumerkey",
        "consumer_secret": "cs_yoursecret",
        "username": "yourusername",
        "password": "yourpassword"
    }
    """
    encryptor = ConfigEncryptor()
    print(f"Encryption key: {encryptor.get_key()}")
    encryptor.encrypt_config(CONFIG_DATA)
