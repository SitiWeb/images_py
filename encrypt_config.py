from cryptography.fernet import Fernet

# Generate a key and print it
key = Fernet.generate_key()
print(f"Encryption key: {key.decode()}")  # Save this key securely

# Function to encrypt the configuration data
def encrypt_config(data, key):
    fernet = Fernet(key)
    encrypted = fernet.encrypt(data.encode())
    with open("config.enc", "wb") as encrypted_file:
        encrypted_file.write(encrypted)

if __name__ == "__main__":
    config_data = """{
        "url": "https://yourstore.com",
        "consumer_key": "ck_yourconsumerkey",
        "consumer_secret": "cs_yoursecret",
        "username": "yourusername",
        "password": "yourpassword"
    }"""
    encrypt_config(config_data, key)
