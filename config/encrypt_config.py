from cryptography.fernet import Fernet

class ConfigEncryptor:
    def __init__(self):
        self.key = Fernet.generate_key()

    def encrypt_config(self, data):
        fernet = Fernet(self.key)
        encrypted = fernet.encrypt(data.encode())
        with open("config.enc", "wb") as encrypted_file:
            encrypted_file.write(encrypted)

    def get_key(self):
        return self.key.decode()

if __name__ == "__main__":
    config_data = """
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
    encryptor.encrypt_config(config_data)
