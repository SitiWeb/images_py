import tkinter as tk
from tkinter import ttk
from api.woocommerce import save_credentials, load_credentials

class SettingsTab:
    def __init__(self, tab_parent, text):
        self.tab = ttk.Frame(tab_parent)
        tab_parent.add(self.tab, text=text)

        self.credentials = load_credentials()
        self.setup_ui()

    def setup_ui(self):
        url_label = tk.Label(self.tab, text="WooCommerce URL:")
        url_label.pack(pady=5)

        self.url_entry = tk.Entry(self.tab)
        self.url_entry.insert(0, self.credentials.get('url', ''))
        self.url_entry.pack(pady=5)

        consumer_key_label = tk.Label(self.tab, text="Consumer Key:")
        consumer_key_label.pack(pady=5)

        self.consumer_key_entry = tk.Entry(self.tab)
        self.consumer_key_entry.insert(0, self.credentials.get('consumer_key', ''))
        self.consumer_key_entry.pack(pady=5)

        consumer_secret_label = tk.Label(self.tab, text="Consumer Secret:")
        consumer_secret_label.pack(pady=5)

        self.consumer_secret_entry = tk.Entry(self.tab, show="*")
        self.consumer_secret_entry.insert(0, self.credentials.get('consumer_secret', ''))
        self.consumer_secret_entry.pack(pady=5)

        username_label = tk.Label(self.tab, text="Username:")
        username_label.pack(pady=5)

        self.username_entry = tk.Entry(self.tab)
        self.username_entry.insert(0, self.credentials.get('username', ''))
        self.username_entry.pack(pady=5)

        password_label = tk.Label(self.tab, text="Password:")
        password_label.pack(pady=5)

        self.password_entry = tk.Entry(self.tab, show="*")
        self.password_entry.insert(0, self.credentials.get('password', ''))
        self.password_entry.pack(pady=5)

        save_button = tk.Button(self.tab, text="Save Credentials", command=self.save_credentials)
        save_button.pack(pady=5)

    def save_credentials(self):
        save_credentials(
            self.url_entry.get(),
            self.consumer_key_entry.get(),
            self.consumer_secret_entry.get(),
            self.username_entry.get(),
            self.password_entry.get()
        )
