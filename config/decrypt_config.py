from cryptography.fernet import Fernet
import json
import os

class ConfigDecryptor:
    def __init__(self, key):
        self.key = key

    def decrypt(self):
        if not os.path.exists("config.enc"):
            raise FileNotFoundError("The encrypted configuration file 'config.enc' does not exist.")
        
        fernet = Fernet(self.key)
        with open("config.enc", "rb") as encrypted_file:
            encrypted = encrypted_file.read()
        decrypted = fernet.decrypt(encrypted).decode()
        return json.loads(decrypted)
# Define your key here
key = b'u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI='  # Replace with your actual key

if __name__ == "__main__":
    key = b'u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI='  # Replace with your actual key
    decryptor = ConfigDecryptor(key)
    try:
        config = decryptor.decrypt()
        print(config)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")
