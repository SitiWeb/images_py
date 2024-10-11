from cryptography.fernet import Fernet
import json
import os


class ConfigEncryptor:
    def __init__(self, key, filename="config.enc"):
        self.key = key
        self.filename = filename
        self.fernet = Fernet(self.key)

    def encrypt_config(self, data):
        """
        Encrypt the given data and save it to a file.
        
        Args:
            data (dict): The dictionary containing credentials and options to encrypt and save.
        """
        try:
            json_data = json.dumps(data)
            encrypted_data = self.fernet.encrypt(json_data.encode())
            with open(self.filename, "wb") as encrypted_file:
                encrypted_file.write(encrypted_data)
                print(f"Encrypted configuration saved to {self.filename}")
        except Exception as e:
            print(f"Error encrypting config: {e}")

    def get_key(self):
        """
        Return the encryption key.
        
        Returns:
            str: The encryption key as a string.
        """
        return self.key.decode()

    def save_credentials(self, credentials):
        """
        Save WooCommerce credentials to the config file, handling multiple credential sets.
        
        Args:
            credentials (dict): Dictionary containing WooCommerce credentials.
        """
        # Load the existing configuration
        config = self.load_config() or {"credentials": [], "options": {}}
        
        # Ensure credentials is a list of dictionaries (if this is the first time saving, initialize it)
        if not isinstance(config.get("credentials"), list):
            config["credentials"] = []
        
        # Check if the credential with the same 'name' or 'nice_name' already exists and update it
        existing_credential = None
        for cred in config["credentials"]:
            print(credentials)
            if cred.get("nice_name") == credentials.get("nice_name"):
                existing_credential = cred
                break
        
        if existing_credential:
            # Update the existing credential set
            existing_credential.update(credentials)
        else:
            # Add new credentials if they don't exist
            config["credentials"].append(credentials)
        
        # Set 'active' flag to True for this credential and False for others
        for cred in config["credentials"]:
            cred['active'] = cred.get("nice_name") == credentials.get("nice_name")

        # Encrypt and save the updated config
        self.encrypt_config(config)
        print(f"Credentials for {credentials.get('nice_name', 'Unnamed')} saved successfully.")

    def delete_credentials(self, credentials):
        """
        Save WooCommerce credentials to the config file, handling multiple credential sets.
        
        Args:
            credentials (dict): Dictionary containing WooCommerce credentials.
        """
        # Load the existing configuration
        config = self.load_config() or {"credentials": [], "options": {}}
        
        new_config = []
        for credi in config["credentials"]:
            
            if credi.get("nice_name") != credentials:
                new_config.append(credi) 
        config["credentials"] = new_config
        print(config)
        # Encrypt and save the updated config
        self.encrypt_config(config)



    def save_options(self, options):
        """
        Save options to the config file. Filters out non-serializable data.
        
        Args:
            options (dict): Dictionary containing options such as canvas width, height, etc.
        """
        config = self.load_config() or {"credentials": {}, "options": {}}
        serializable_options = {k: v for k, v in options.items() if self.is_json_serializable(v)}
        config["options"] = serializable_options
        self.encrypt_config(config)

    def load_config(self):
        """
        Load and decrypt the config file.
        
        Returns:
            dict: Decrypted configuration data containing credentials and options, or None if file not found.
        """
        if not os.path.exists(self.filename):
            print(f"Config file {self.filename} not found.")
            return None

        try:
            with open(self.filename, "rb") as encrypted_file:
                encrypted_data = encrypted_file.read()
            decrypted_data = self.fernet.decrypt(encrypted_data).decode()
            config = json.loads(decrypted_data)
            return config
        except Exception as e:
            print(f"Error loading or decrypting config: {e}")
            return None

    def load_credentials(self):
        """
        Load the active WooCommerce credentials from the config file.
        
        Returns:
            dict: The active WooCommerce credentials if found, otherwise None.
        """
        config = self.load_config()
        if config:
            # Check if credentials exist and search for the one marked as 'active'
            credentials_list = config.get("credentials", [])
            if isinstance(credentials_list, list):
                for credentials in credentials_list:
                    if credentials.get("active"):
                        return credentials
            elif isinstance(credentials_list, dict):
                return credentials_list
        return None


    @staticmethod
    def is_json_serializable(value):
        """
        Check if a value is JSON serializable.
        
        Args:
            value: The value to check.
        
        Returns:
            bool: True if value is serializable, False otherwise.
        """
        try:
            json.dumps(value)
            return True
        except (TypeError, OverflowError):
            return False


# Define your key here
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
