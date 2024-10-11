import customtkinter as ctk
from api.woocommerce_api import (
    load_credentials,
    save_active_credential_set,
)
from config.encrypt_config import ConfigEncryptor
from PIL import Image, ImageTk

import os
import sys
KEY = b"u4xTBY5Ns4WYdLvqMjEr138mpMmDEhhqTszKCcDy2cI="
def resource_path(relative_path):
    """ Get the absolute path to a resource, whether we're running in development or a PyInstaller package. """
    try:
        # PyInstaller stores files in _MEIPASS when built
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, 'ui/images/'+ relative_path +'.png')

class SettingsTab:
    def __init__(self, tab_parent, controller):
        self.tab = ctk.CTkFrame(tab_parent)
        self.tab.grid(row=0, column=0, sticky="nsew")
         # Initialize an instance of ConfigEncryptor
        self.config_encryptor = ConfigEncryptor(KEY)  # Ensure you pass any required arguments in the constructor if necessary
        config = self.config_encryptor.load_config()
        self.credentials_list = []
        if config:
            self.credentials_list = self.config_encryptor.load_config().get('credentials') 
            self.active_credential_set = (
                self.get_active_credential_set()
            )  # Fetch active credentials
        else:
            self.active_credential_set = {
                'nice_name': "Default"
            }
        self.inputs = {}
        self.setup_ui()

    def get_active_credential_set(self):
        """Retrieve active credential set from saved data and convert to new format if needed."""
        if isinstance(self.credentials_list, list) and all(
            isinstance(cred, dict) for cred in self.credentials_list
        ):
            for cred in self.credentials_list:
                if cred.get("active", False):
                    return cred
            return self.credentials_list[0] if self.credentials_list else None

        elif isinstance(self.credentials_list, dict):
            self.credentials_list = [self.convert_to_new_format(self.credentials_list)]
            return self.credentials_list[0]

        elif isinstance(self.credentials_list, str):
            self.credentials_list = [
                self.convert_to_new_format({"url": self.credentials_list})
            ]
            return self.credentials_list[0]

        return None

    def convert_to_new_format(self, old_credential):
        return {
            "url": old_credential.get("url", ""),
            "consumer_key": old_credential.get("consumer_key", ""),
            "consumer_secret": old_credential.get("consumer_secret", ""),
            "username": old_credential.get("username", ""),
            "password": old_credential.get("password", ""),
            "name": old_credential.get("name", "Default Credential Set"),
            "nice_name": old_credential.get("nice_name", old_credential.get("url", "Unnamed Credential")),
            "active": True,
        }

    def setup_ui(self):
        # Dropdown to select active credentials
        self.credential_var = ctk.StringVar()
        self.credential_var.set(
            self.active_credential_set.get("nice_name", "Default")
        )
        credential_options = [
            cred.get("nice_name", "Unnamed Credential")
            for cred in self.credentials_list
        ]

        dropdown_label = ctk.CTkLabel(self.tab, text="Select Active Credentials:")
        dropdown_label.grid(row=0, column=0, padx=5, columnspan=2 , pady=5, sticky="w")
        self.credential_dropdown = ctk.CTkComboBox(
            self.tab,
            variable=self.credential_var,
            values=credential_options,
            command=self.load_selected_credential,
        )
        self.credential_dropdown.grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky="w")

        # Show fields for credentials
        self.create_credentials_form(self.active_credential_set, row_index=1)
        
        icon_path = resource_path("save")
        icon_image = ctk.CTkImage(light_image=Image.open(icon_path), size=(24, 24)) if icon_path else None

        save_button = ctk.CTkButton(
            self.tab, width=100,fg_color="green",image=icon_image, text="Save", command=self.save_credentials
        )
        save_button.grid(row=7, column=0, columnspan=1, pady=10)

        new_button = ctk.CTkButton(
            self.tab, width=100, fg_color="green", image=icon_image, text="New", command=self.add_new_credential_set
        )
        new_button.grid(row=7, column=1, columnspan=1, pady=10)

        # Trash icon for delete button
        trash_icon_path = resource_path("trash")
        trash_icon_image = ctk.CTkImage(light_image=Image.open(trash_icon_path), size=(24, 24)) if trash_icon_path else None

        delete_button = ctk.CTkButton(
            self.tab, width=100, fg_color="red", image=trash_icon_image, text="Delete", command=self.delete_selected_credential
        )
        delete_button.grid(row=7, column=2, columnspan=1, pady=10)

    def create_credentials_form(self, credentials, row_index):
        settings_options = {
            "url": {
                "type": "text",
                "label": "WooCommerce URL:",
                "default": credentials.get("url", ""),
            },
            "consumer_key": {
                "type": "text",
                "label": "Consumer Key:",
                "default": credentials.get("consumer_key", ""),
            },
            "consumer_secret": {
                "type": "text",
                "label": "Consumer Secret:",
                "default": credentials.get("consumer_secret", ""),
            },
            "username": {
                "type": "text",
                "label": "Username:",
                "default": credentials.get("username", ""),
            },
            "password": {
                "type": "text",
                "label": "Password:",
                "default": credentials.get("password", ""),
                "show": "*",
            },
            "nice_name": {
                "type": "text",
                "label": "Nice Name:",
                "default": credentials.get("nice_name", "Unnamed Credential"),
            },
        }

        self.inputs = {}  # Reset inputs for new credentials set
        for name, details in settings_options.items():
            self.create_setting(name, details, row_index)
            row_index += 1

    def create_setting(self, name, details, row_index):
        lbl = ctk.CTkLabel(self.tab, text=details["label"])
        lbl.grid(row=row_index, column=0,columnspan=2, padx=5, pady=5, sticky="w")

        entry = ctk.CTkEntry(self.tab, show=details.get("show", None))
        entry.insert(0, details["default"])
        entry.grid(row=row_index, column=2,columnspan=2, padx=5, pady=5, sticky="w")
        self.inputs[name] = entry

    def load_selected_credential(self, selected_name):
        for cred in self.credentials_list:
            if cred.get("nice_name", "Unnamed Credential") == selected_name:
                self.active_credential_set = cred
                self.create_credentials_form(self.active_credential_set, row_index=1)
                break

    def save_credentials(self):
        credentials = {
            "url": self.inputs["url"].get(),
            "consumer_key": self.inputs["consumer_key"].get(),
            "consumer_secret": self.inputs["consumer_secret"].get(),
            "username": self.inputs["username"].get(),
            "password": self.inputs["password"].get(),
            "name": self.inputs["nice_name"].get(),
            "nice_name": self.inputs["nice_name"].get(),
            "active": True,
        }

        ConfigEncryptor(KEY).save_credentials(credentials)
        save_active_credential_set(credentials["name"])

        self.credentials_list.append(credentials)
        self.credential_dropdown.configure(
            values=[cred.get("nice_name", "Unnamed Credential") for cred in self.credentials_list]
        )

    def add_new_credential_set(self):
        self.active_credential_set = {
            "url": "",
            "consumer_key": "",
            "consumer_secret": "",
            "username": "",
            "password": "",
            "name": "New Credential Set",
            "nice_name": "New Credential Set",
            "active": False,
        }
        self.create_credentials_form(self.active_credential_set, row_index=1)
        self.credential_var.set(self.active_credential_set["nice_name"])

    def delete_selected_credential(self):
        selected_name = self.credential_var.get()

        # Find and remove the selected credential from the list
        self.credentials_list = [
            cred for cred in self.credentials_list if cred.get("nice_name") != selected_name
        ]

        # Save updated credentials list to storage
        ConfigEncryptor(KEY).delete_credentials(selected_name)

        # Update the dropdown and form after deletion
        if self.credentials_list:
            self.active_credential_set = self.credentials_list[0]  # Load first available credential
            self.credential_var.set(self.active_credential_set["nice_name"])
            self.create_credentials_form(self.active_credential_set, row_index=1)
        else:
            self.active_credential_set = {}
            self.create_credentials_form({}, row_index=1)  # Clear form if no credentials are left

        self.credential_dropdown.configure(
            values=[cred.get("nice_name", "Unnamed Credential") for cred in self.credentials_list]
        )
