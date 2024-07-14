import customtkinter as ctk
from api.woocommerce_api import save_credentials, load_credentials

class SettingsTab:
    def __init__(self, tab_parent):
        self.tab = ctk.CTkFrame(tab_parent)
        self.tab.grid(row=0, column=0, sticky="nsew")
        self.credentials = load_credentials()
        self.inputs = {}
        self.setup_ui()

    def setup_ui(self):
        settings_options = {
            "url": {"type": "text", "label": "WooCommerce URL:", "default": self.credentials.get('url', '')},
            "consumer_key": {"type": "text", "label": "Consumer Key:", "default": self.credentials.get('consumer_key', '')},
            "consumer_secret": {"type": "text", "label": "Consumer Secret:", "default": self.credentials.get('consumer_secret', '')},
            "username": {"type": "text", "label": "Username:", "default": self.credentials.get('username', '')},
            "password": {"type": "text", "label": "Password:", "default": self.credentials.get('password', ''), "show": "*"}
        }

        row_index = 0
        for name, details in settings_options.items():
            self.create_setting(name, details, row_index)
            row_index += 1

        save_button = ctk.CTkButton(self.tab, text="Save Credentials", command=self.save_credentials)
        save_button.grid(row=row_index, column=0, columnspan=2, pady=10)

    def create_setting(self, name, details, row_index):
        """
        Create a setting based on its type.
        """
        lbl = ctk.CTkLabel(self.tab, text=details["label"])
        lbl.grid(row=row_index, column=0, padx=5, pady=5, sticky="w")

        if details["type"] == "text":
            entry = ctk.CTkEntry(self.tab, show=details.get("show", None))
            entry.insert(0, details["default"])
            entry.grid(row=row_index, column=1, padx=5, pady=5, sticky="w")
            self.inputs[name] = entry

    def save_credentials(self):
        save_credentials(
            self.inputs["url"].get(),
            self.inputs["consumer_key"].get(),
            self.inputs["consumer_secret"].get(),
            self.inputs["username"].get(),
            self.inputs["password"].get()
        )
