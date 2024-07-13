from cryptography.fernet import Fernet
import json
import os

# Hardcoded key (replace with your generated key)
key = b'u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI='

def decrypt_config(key):
    if not os.path.exists("config.enc"):
        raise FileNotFoundError("The encrypted configuration file 'config.enc' does not exist.")
    
    fernet = Fernet(key)
    with open("config.enc", "rb") as encrypted_file:
        encrypted = encrypted_file.read()
    decrypted = fernet.decrypt(encrypted).decode()
    return json.loads(decrypted)

if __name__ == "__main__":
    try:
        config = decrypt_config(key)
        print(config)  # Use the decrypted config
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")
