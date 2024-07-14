from cryptography.fernet import Fernet
import json


class ConfigEncryptor:
    def __init__(self, key, filename="config.enc"):
        self.key = key
        self.filename = filename
        self.fernet = Fernet(self.key)

    def encrypt_config(self, data):
        json_data = json.dumps(data)
        encrypted_data = self.fernet.encrypt(json_data.encode())
        with open(self.filename, "wb") as encrypted_file:
            encrypted_file.write(encrypted_data)
            print("Credentials saved")

    def get_key(self):
        return self.key.decode()

    def save_credentials(self, credentials):
        config = self.load_config()
        if not config:
            config = {"credentials": {}, "options": {}}
        config["credentials"] = credentials
        self.encrypt_config(config)

    def save_options(self, options):
        config = self.load_config()
        if not config:
            config = {"credentials": {}, "options": {}}
        # Ensure options only contains serializable data
        serializable_options = {k: v for k, v in options.items() if self.is_json_serializable(v)}
        config["options"] = serializable_options
        self.encrypt_config(config)

    def load_config(self):
        try:
            with open(self.filename, "rb") as encrypted_file:
                encrypted_data = encrypted_file.read()
            decrypted_data = self.fernet.decrypt(encrypted_data).decode()
            config = json.loads(decrypted_data)
            
            # Filter only relevant keys
            keys_to_return = ["credentials", "options"]
            return {key: config[key] for key in keys_to_return if key in config}
        except FileNotFoundError:
            return None
    def load_credentials(self):
        config = self.load_config()
        if config:
            return config.get("credentials")
        return None

    @staticmethod
    def is_json_serializable(value):
        try:
            json.dumps(value)
            return True
        except (TypeError, OverflowError):
            return False


# Define your key here
# Replace with your actual key
key = b"u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI="

if __name__ == "__main__":
    config_data = {
        "credentials": {
            "url": "https://yourstore.com",
            "consumer_key": "ck_yourconsumerkey",
            "consumer_secret": "cs_yoursecret",
            "username": "yourusername",
            "password": "yourpassword"
        },
        "options": {
            "canvas_width": 900,
            "canvas_height": 900,
            "template": "{slug}_{sku}_{width}x{height}",
            "delete_images": False,
            "background_color": "#FFFFFF"
        }
    }
    encryptor = ConfigEncryptor(key)
    encryptor.encrypt_config(config_data)

