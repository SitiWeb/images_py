import tkinter as tk
from tkinter import ttk
from api.woocommerce import save_credentials, load_credentials

def create_tab_settings(tab_parent, text):
    tab = ttk.Frame(tab_parent)
    tab_parent.add(tab, text=text)

    credentials = load_credentials()
    url_value = credentials['url'] if credentials else ''
    consumer_key_value = credentials['consumer_key'] if credentials else ''
    consumer_secret_value = credentials['consumer_secret'] if credentials else ''
    username_value = credentials['username'] if credentials else ''
    password_value = credentials['password'] if credentials else ''
    
    url_label = tk.Label(tab, text="WooCommerce URL:")
    url_label.pack(pady=5)
    
    url_entry = tk.Entry(tab)
    url_entry.insert(0, url_value)
    url_entry.pack()
    
    consumer_key_label = tk.Label(tab, text="Consumer Key:")
    consumer_key_label.pack(pady=5)
    
    consumer_key_entry = tk.Entry(tab)
    consumer_key_entry.insert(0, consumer_key_value)
    consumer_key_entry.pack()
    
    consumer_secret_label = tk.Label(tab, text="Consumer Secret:")
    consumer_secret_label.pack(pady=5)
    
    consumer_secret_entry = tk.Entry(tab, show="*")
    consumer_secret_entry.insert(0, consumer_secret_value)
    consumer_secret_entry.pack()
    
    username_label = tk.Label(tab, text="Username:")
    username_label.pack(pady=5)
    
    username_entry = tk.Entry(tab)
    username_entry.insert(0, username_value)
    username_entry.pack()
    
    password_label = tk.Label(tab, text="Password:")
    password_label.pack(pady=5)
    
    password_entry = tk.Entry(tab, show="*")
    password_entry.insert(0, password_value)
    password_entry.pack()
    
    button_save = tk.Button(tab, text="Save Credentials", command=lambda: save_credentials(
        url_entry.get(),
        consumer_key_entry.get(),
        consumer_secret_entry.get(),
        username_entry.get(),
        password_entry.get()
    ))
    button_save.pack(pady=5)
